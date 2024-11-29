import asyncio
import aiohttp
from typing import Union
from datetime import datetime, UTC, timedelta, timezone
from bs4 import BeautifulSoup

from shared.models import TvParser, TvProgramData
from shared.options import SaveOptions, read_command_line_options
from shared.output import run_parser_out_to_csv
from shared.utils import fill_finish_date_by_next_start_date, get_monday_datetime, get_node_text, is_none_or_empty, replace_spaces

class HaberGlobalParser(TvParser):
    __source_url = "https://tv41.com.tr/yayin-akisi/"
    __channel_name = "TV41"
    __channel_logo_url = None
    __response_time_zone = timezone(timedelta(hours=3))

    async def parse_async(self) -> list[TvProgramData]:
        async with aiohttp.ClientSession() as session:
            async with session.get(self.__source_url) as resp:
                html_text = await resp.text()
                return self.__parse_html(html_text)

    def __parse_html(self, html_input: str):
        html = BeautifulSoup(html_input, 'html.parser')
        day_info = html.find("div", {"class": "entry-content-inner"}).find_all("p")

        date = day_info[0].text
        day_programs = day_info[1:]

        current_day =self.__parse_date(date)
        parsed_programs = self.__parse_day_programs(day_programs, current_day)
        

        fill_finish_date_by_next_start_date(parsed_programs)        
        return parsed_programs

    def __parse_day_programs(self, day_programs, current_day):
        parsed_programs = []
        last_hour = 0

        for program_info in day_programs:
            program_info = replace_spaces(program_info.text)
            if (len(program_info) == 0):
                continue

            datetime_start = self.__parse_time(
                program_info[0:9], 
                current_day
            )

            if (last_hour > datetime_start.hour):
                datetime_start += timedelta(days=1)
                current_day += timedelta(days=1)
            last_hour = datetime_start.hour

            show_name = replace_spaces(program_info[9:])

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
    
    def __parse_date(self, date) -> datetime:
        return datetime.strptime(date, "%d.%m.%Y").replace(
            tzinfo=self.__response_time_zone
        )

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
