import asyncio
import aiohttp
from typing import Tuple, Union
from datetime import datetime, UTC, timedelta, timezone
from bs4 import BeautifulSoup

from shared.models import TvParser, TvProgramData
from shared.options import SaveOptions, read_command_line_options
from shared.output import run_parser_out_to_csv
from shared.utils import fill_finish_date_by_next_start_date, get_monday_datetime, get_node_text, is_none_or_empty, replace_spaces

class EkolTvParser(TvParser):
    __source_url = "https://www.ekoltv.com.tr/yayin-akisi"
    __channel_name = "Ekol TV"
    __channel_logo_url = None
    __response_time_zone = timezone(timedelta(hours=3))
    __remove_last = True

    async def parse_async(self) -> list[TvProgramData]:
        async with aiohttp.ClientSession() as session:
            http_urls = self.get_day_urls()    

            parsed_days_result = await asyncio.gather(*[
                self.parse_day_async(session, url) for url in http_urls 
            ])

            sorted_by_dates = sorted(parsed_days_result, key=lambda x: x[0])
            
            result = [ 
                program 
                for day in sorted_by_dates 
                    for program in day[1]
            ]            
        
            fill_finish_date_by_next_start_date(result, self.__remove_last)
            
            return result

    async def parse_day_async(self, session, http_url) -> Tuple[datetime, list[TvProgramData]]:
        date_from_url = http_url.split("=")[-1]
        current_day = datetime.strptime(date_from_url, "%d.%m.%Y").replace(tzinfo=self.__response_time_zone)

        async with session.get(http_url) as resp: 
            return self.parse_day_html(await resp.text(), current_day)
        
    def parse_day_html(self, html_text:str, current_day:datetime):
        html = BeautifulSoup(html_text, 'html.parser')
        parsed_programs = []

        programs = html.find("div", {"class":"tl-list"}).find_all("div", recursive=False)
        last_hour = 0

        for program in programs:
            program = program.div
            time = program.find("span",{"class": "time"}).next.split(":")
            hours = int(time[0])
            minutes = int(time[1])

            program_name = get_node_text(program.find("a",{"class": "title"}))

            if (last_hour > hours):
                current_day += timedelta(days=1)
            last_hour = hours

            datetime_start = current_day.replace(
                hour=hours,
                minute=minutes,
                second=0,
                tzinfo=self.__response_time_zone
            )

            tv_program = TvProgramData(
                datetime_start,
                None,
                self.__channel_name,
                program_name,
                self.__channel_logo_url,
                None,
                False
            )

            parsed_programs.append(tv_program)

        return (current_day, parsed_programs)
    
    
    def get_day_urls(self) -> list[str]:
        monday = get_monday_datetime(self.__response_time_zone)
        day_urls = []

        for day_index in range(0, 7):
            day = monday + timedelta(days=day_index)
            day_urls.append(
                self.__source_url + f"?date={day.day}.{day.month}.{day.year}"
            )

        return day_urls
    
    def parse_time(self, time_str: str) -> datetime:
        return datetime.fromisoformat(time_str)




if (__name__=="__main__"):
    options = read_command_line_options()
    parser = EkolTvParser(options.parser_options)
    run_parser_out_to_csv(parser, options.save_options)
