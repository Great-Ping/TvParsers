import asyncio
import aiohttp
from typing import Union
from datetime import datetime, UTC, timedelta, timezone
from bs4 import BeautifulSoup

from shared.models import TvParser, TvProgramData
from shared.options import SaveOptions, read_command_line_options
from shared.output import run_parser_out_to_csv
from shared.utils import fill_finish_date_by_next_start_date, get_monday_datetime, get_node_text, is_none_or_empty

class HaberGlobalParser(TvParser):
    __source_url = "https://www.ekoltv.com.tr/yayin-akisi"
    __channel_name = "Ekol TV"
    __channel_logo_url = None
    __response_time_zone = timezone(timedelta(hours=3))

    async def parse_async(self) -> list[TvProgramData]:
        async with aiohttp.ClientSession() as session:
            async with session.get(self.__source_url) as resp:
                html_text = await resp.text()
                return self.__parse_html(html_text)

    def __parse_html(self, html_input: str):
        html = BeautifulSoup(html_input, 'html.parser')
        program_days = html.find("div", {"id": "pills-tabContent"})
        parsed_programs = []

        current_day = get_monday_datetime(self.__response_time_zone)
        for current_day_programs in program_days.find_all("div", recursive=False):
            parsed_programs.extend(
                self.__parse_day_programs(current_day_programs.div, current_day)
            )
            current_day += timedelta(days=1)

        fill_finish_date_by_next_start_date(parsed_programs)        
        return parsed_programs

    def __parse_day_programs(self, current_day_programs, current_day):
        parsed_programs = []
        for program_info in current_day_programs.find_all("div", recursive=False):
            program_info = program_info.a
            datetime_start = self.__parse_time(
                program_info.find("h4").text, 
                current_day
            )
            show_name = self.__replace_spaces(program_info.find("h5").text)

            parsed_programs.append(TvProgramData(
                datetime_start,
                None,
                self.__channel_name,
                show_name,
                self.__channel_logo_url,
                None,
                False
            ))

        return parsed_programs

    def __replace_spaces(self, string: str):
        start = 0
        end = len(string)
        for i in string:
            if (not is_none_or_empty(i)):
                break
            start += 1

        for i in reversed(string):
            if (not is_none_or_empty(i)):
                break
            end -= 1
        
        return string[start: end]


    def __parse_time(self, time, current_day) -> datetime:
        day = time.split(":") #20:00
        return current_day.replace(
            hour=int(day[0]),
            minute=int(day[1]),
            second=0,
            tzinfo=self.__response_time_zone
        )




if (__name__=="__main__"):
    options = read_command_line_options()
    parser = HaberGlobalParser(options.parser_options)
    run_parser_out_to_csv(parser, options.save_options)