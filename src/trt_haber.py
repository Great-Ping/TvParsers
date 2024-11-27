
import asyncio
import aiohttp
from datetime import datetime, UTC, timedelta, timezone
from bs4 import BeautifulSoup

from shared.options import SaveOptions, read_command_line_options
from shared.models import TvParser, TvProgramData
from shared.output import run_parser_out_to_csv
from shared.utils import fill_finish_date_by_next_start_date, get_monday_datetime, is_none_or_empty

class TrtHaberParser(TvParser):
    __source_url = "https://www.trthaber.com/yayin-akisi.html" 
    __channel_name = "TRT HABER"
    __channel_logo_url = None
    __response_time_zone = timezone(timedelta(hours=3))

    async def parse_async(self) -> list[TvProgramData]:
        async with aiohttp.ClientSession() as session:
            http_urls:list[str]

            async with session.get(self.__source_url) as resp:
                http_urls = self.get_day_urls(await resp.text())    

            parsed_days_result = await asyncio.gather(*[
                self.parse_day_async(session, url) for url in http_urls 
            ])

            sorted_by_dates = sorted(parsed_days_result, key=lambda x: x[0])
            
            result = [ 
                program 
                for day in sorted_by_dates 
                    for program in day[1]
            ]            
        
            fill_finish_date_by_next_start_date(result)
            
            return result

    async def parse_day_async(self, session, http_url) -> (datetime, list[TvProgramData]):
        date_from_url = http_url.split("/")[-1]
        current_day = datetime.strptime(date_from_url, "%d-%m-%Y").replace(tzinfo=self.__response_time_zone)

        async with session.get(http_url) as resp: 
            return self.parse_day_html(await resp.text(), current_day)

    def parse_day_html(self, html_text:str, current_day:datetime):
        html = BeautifulSoup(html_text, 'html.parser')
        parsed_programs = []

        programs = html.find("ul", {"class":"epg-list"}).find_all("li", recursive=False)
        prev_hour = 0

        for program in programs:
           
            time = program.find("div",{"class": "time"}).next.split(":")

            hours = int(time[0])
            minutes = int(time[1])

            program_name = program.find("div",{"class": "program-name"}).next

            if (prev_hour > hours):
                current_day += timedelta(days=1)
            prev_hour = hours

            datetime_start = current_day.replace(
                hour=hours,
                minute=minutes,
                second=0,
                tzinfo=self.__response_time_zone
            )
            
            parsed_programs.append(TvProgramData(
                datetime_start,
                None,
                self.__channel_name,
                program_name,
                self.__channel_logo_url,
                None,
                False
            ))

        return (current_day, parsed_programs)

    
    def get_day_urls(self, html_text) -> list[str]:
        html = BeautifulSoup(html_text, 'html.parser')
        days_list = html.find("ul", {"class": "days-list"})
        a_tags = days_list.find_all("a")

        return [a_tag.attrs["href"] for a_tag in a_tags]
    
    def parse_time(self, time_str: str) -> datetime:
        return datetime.fromisoformat(time_str)
if (__name__=="__main__"):
    options = read_command_line_options()
    parser = TrtHaberParser(options.parser_options)
    run_parser_out_to_csv(parser, options.save_options)