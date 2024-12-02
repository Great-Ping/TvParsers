import asyncio
import aiohttp
from typing import Union
from datetime import datetime, UTC, timedelta, timezone
from bs4 import BeautifulSoup

from shared.models import TvParser, TvProgramData
from shared.options import SaveOptions, read_command_line_options
from shared.output import run_parser_out_to_csv
from shared.utils import fill_finish_date_by_next_start_date, get_monday_datetime, get_node_text, is_none_or_empty, replace_spaces

class CanTvParser(TvParser):
    __source_url = "https://cantv.tv/yayin-akisi/"
    __channel_name = "Can tv"
    __channel_logo_url = None
    __response_time_zone = timezone(timedelta(hours=3))

    async def parse_async(self) -> list[TvProgramData]:
        async with aiohttp.ClientSession() as session:
            async with session.get(self.__source_url) as resp:
                html_text = await resp.text()
                return self.__parse_html(html_text)

    def __parse_html(self, html_input: str):
        html = BeautifulSoup(html_input, 'html.parser')
        program_days = html.find("div", {"class": "vc_tta-panels"})
        parsed_programs = []

        current_day = get_monday_datetime(self.__response_time_zone)
        for current_day_programs in program_days.find_all("p"):
            parsed_programs.extend(
                self.__parse_day_programs(current_day_programs, current_day)
            )
            current_day += timedelta(days=1)
   
        return parsed_programs

    def __parse_day_programs(self, current_day_programs, current_day):
        parsed_programs = []
        for program_info in current_day_programs.text.split("\n"):
            if (is_none_or_empty(program_info)):
                continue

            program_info = replace_spaces(program_info)
            datetime_start = self.__parse_time(
                program_info[0:5], 
                current_day
            )
            show_name = replace_spaces(program_info[5:])

            parsed_programs.append(TvProgramData(
                datetime_start,
                None,
                self.__channel_name,
                show_name,
                self.__channel_logo_url,
                None,
                False
            ))
            
        fill_finish_date_by_next_start_date(parsed_programs)  
        self.__try_set_bu_subhal_datetime(parsed_programs)
        return parsed_programs

    def __try_set_bu_subhal_datetime(self, parsed_programs):
        for program in parsed_programs:
            if (program.title == 'BU SABAH II'):
                program.datetime_finish = program.datetime_start + timedelta(hours=1)


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
    parser = CanTvParser(options.parser_options)
    run_parser_out_to_csv(parser, options.save_options)
