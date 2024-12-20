import asyncio
import aiohttp
from typing import Union
from datetime import datetime, UTC, timedelta, timezone
from bs4 import BeautifulSoup

from shared.models import TvParser, TvProgramData
from shared.options import SaveOptions, read_command_line_options
from shared.output import run_parser_out_to_csv
from shared.utils import fill_finish_date_by_next_start_date, get_monday_datetime, get_node_text, is_none_or_empty, replace_spaces

class Kanal3Parser(TvParser):
    __source_url = "https://kanal3.com.tr/yayin-akisi/"
    __channel_name = "kANAL 3"
    __channel_logo_url = None
    __response_time_zone = timezone(timedelta(hours=3))
    __remove_last = True

    async def parse_async(self) -> list[TvProgramData]:
        async with aiohttp.ClientSession() as session:
            async with session.get(self.__source_url) as resp:
                html_text = await resp.text()
                return self.__parse_html(html_text)

    def __parse_html(self, html_input: str):
        html = BeautifulSoup(html_input, 'html.parser')
        programs = html.find_all("div", {"class": "sow-tabs-panel"})
        parsed_programs = []
        current_day = get_monday_datetime(self.__response_time_zone)

        for day_programs in programs:
            parsed_programs.extend(
                self.__parse_day_programs(day_programs.find("tbody"), current_day)
            )
            current_day += timedelta(days=1)
            
        fill_finish_date_by_next_start_date(parsed_programs, self.__remove_last)        
        return parsed_programs
    
    def __parse_time(self, time, current_day) -> datetime:
        day = time.split(":") #20:00
        return current_day.replace(
            hour=int(day[0]),
            minute=int(day[1]),
            second=0,
            tzinfo=self.__response_time_zone
        )

    def __parse_day_programs(self, day_programs, current_day):
        parsed_programs = []

        for program in day_programs.find_all("tr", recursive=False):
            program = program.find_all("td")
            datetime_start = self.__parse_time(
                program[0].text, 
                current_day
            )
            show_name = replace_spaces(program[1].text)

            parsed_programs.append(TvProgramData(
                datetime_start,
                None,
                self.__channel_name,
                show_name,
                self.__channel_logo_url,
                None,
                False
            ))
        
        return sorted(parsed_programs, key=lambda x: x.datetime_start)

if (__name__=="__main__"):
    options = read_command_line_options()
    parser = Kanal3Parser(options.parser_options)
    run_parser_out_to_csv(parser, options.save_options)
