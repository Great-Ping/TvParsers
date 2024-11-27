import asyncio
import aiohttp
from datetime import datetime, UTC, timedelta, timezone
from bs4 import BeautifulSoup

from shared.options import SaveOptions, read_command_line_options
from shared.models import TvParser, TvProgramData
from shared.output import run_parser_out_to_csv
from shared.utils import fill_finish_date_by_next_start_date

class TrtBelgeselParser(TvParser):
    __source_url = "https://www.trtbelgesel.com.tr/" 
    __channel_name = "TRT belgesel"
    __channel_logo_url = None
    __response_time_zone = timezone(timedelta(hours=3))

    async def parse_async(self) -> list[TvProgramData]:
        async with aiohttp.ClientSession() as session:
            async with session.get(self.__source_url) as resp:
                current_day = datetime.now(self.__response_time_zone) 
                result = self.parse_day_html(await resp.text(), current_day)
                fill_finish_date_by_next_start_date(result)
                return result

    def parse_day_html(self, html_text:str, current_day:datetime):
        html = BeautifulSoup(html_text, 'html.parser')
        parsed_programs = []

        programs = html.find("div", {"id":"epg"}).find_all("a")
        prev_hour = 0

        for program in programs:
           
            time = program.attrs["data-time"].split(":")
            
            #У текущей телепередачи нет даты и времени
            if len(time) == 1:
                hours = current_day.hour
                minutes = current_day.minute
            else: 
                hours = int(time[0])
                minutes = int(time[1])

            program_name = program.next.next

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

        return parsed_programs
    
    def parse_time(self, time_str: str) -> datetime:
        return datetime.fromisoformat(time_str)
    
if (__name__=="__main__"):
    options = read_command_line_options()
    parser = TrtBelgeselParser(options.parser_options)
    run_parser_out_to_csv(parser, options.save_options)