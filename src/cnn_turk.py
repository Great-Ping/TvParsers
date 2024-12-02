import asyncio
import aiohttp
from datetime import datetime, UTC, timedelta, timezone
from bs4 import BeautifulSoup

from shared.options import SaveOptions, read_command_line_options
from shared.models import TvParser, TvProgramData
from shared.output import run_parser_out_to_csv
from shared.utils import fill_finish_date_by_next_start_date, get_monday_datetime, get_node_text

class CnnTurkParser(TvParser):
    __source_url = "https://www.cnnturk.com/yayin-akisi/" 
    __channel_name = "cnn türk"
    __channel_logo_url = None
    __response_time_zone = timezone(timedelta(hours=3))
    __remove_last = True

    async def parse_async(self) -> list[TvProgramData]:
        async with aiohttp.ClientSession() as session:
            async with session.get(self.__source_url) as resp:
                result = self.__parse_html(await resp.text())    

            fill_finish_date_by_next_start_date(result, self.__remove_last)
            return result

    def __parse_html(self, html_text:str):
        html = BeautifulSoup(html_text, 'html.parser')
        parsed_programs = []

        program_days = html.find("div", {"class":"tab-content"})
        current_day = get_monday_datetime(self.__response_time_zone)

        for day_programs in program_days.find_all("div", {"class":"tab-item"}):
            parsed_programs.extend(
               self.__parse_day(day_programs, current_day)
            )
            current_day += timedelta(days=1)

        return parsed_programs

    def __parse_day(self, day_programs, current_day):
        parsed_programs = []
        last_hour = 0

        for program in day_programs.children:
            parsed_program = self.__parse_program(program, current_day)
            if (parsed_program.datetime_start.hour < last_hour):
                current_day += timedelta(days=1)
                parsed_program.datetime_start += timedelta(days=1)
            
            last_hour = parsed_program.datetime_start.hour
            parsed_programs.append(parsed_program)

        return parsed_programs

    def __parse_program(self, program, current_day) -> TvProgramData:
            time = program.find("div",{"class": "time"})
            datetime_start = self.select_start_time(time, current_day)
            program_name = program.find("h2",{"class": "title"}).next
            description = get_node_text(program.find("div", {"class": "card-footer"}).p)
            
            return TvProgramData(
                datetime_start,
                None,
                self.__channel_name,
                program_name,
                self.__channel_logo_url,
                description,
                False
            )
    
    def select_start_time(self, time_tag, current_day) -> datetime:
        if (time_tag != None):
            time = time_tag.next.split(":")
            hours = int(time[0])
            minutes = int(time[1])  
            return current_day.replace(
                hour=hours,
                minute=minutes,
                second=0,
                tzinfo=self.__response_time_zone
            )
        
        return current_day
    

if (__name__=="__main__"):
    options = read_command_line_options()
    parser = CnnTurkParser(options.parser_options)
    run_parser_out_to_csv(parser, options.save_options)