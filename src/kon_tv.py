
import asyncio
import aiohttp
from datetime import datetime, UTC, timedelta, timezone
from bs4 import BeautifulSoup

from shared.options import SaveOptions, read_command_line_options
from shared.models import TvParser, TvProgramData
from shared.output import run_parser_out_to_csv
from shared.utils import fill_finish_date_by_next_start_date, get_monday_datetime, get_node_text, is_none_or_empty

class KonTvParser(TvParser):
    __source_url = "https://www.kontv.com.tr/yayin-akisi"
    __channel_name = "kon tv"
    #__channel_logo_url = "https://www.semerkandtv.com.tr/Content/img/logo.png"
    __channel_logo_url = None
    __response_time_zone = timezone(timedelta(hours=3))

    async def parse_async(self) -> list[TvProgramData]:
        async with aiohttp.ClientSession() as session:
            async with session.get(self.__source_url) as resp:
                html_text = await resp.text()
                return self.__parse_html(html_text)

    def __parse_html(self, html_input: str):
        html = BeautifulSoup(html_input, 'html.parser')
        program_days = html.find("ul", {"class": "akisIcerigi"})
        parsed_programs = []
        
        current_day = get_monday_datetime(self.__response_time_zone)
        for current_day_programs in program_days.find_all("li"):
            parsed_programs.extend(
                self.__parse_day_programs(current_day_programs, current_day)
            )
            current_day += timedelta(days=1)
            parsed_programs = sorted(
                parsed_programs,
                key=lambda x: x.datetime_start
            )

        fill_finish_date_by_next_start_date(parsed_programs)        

        return parsed_programs

    def __parse_day_programs(self, current_day_programs, current_day):
        parsed_programs = []
        last_hour = 0
        for program_info in current_day_programs.text.split("\r\n"):
            program_info = program_info.split("\xa0\xa0\xa0\xa0 ")
            if (len(program_info) <= 1):
                continue

            datetime_start = self.__parse_time(program_info[0], current_day)       
            show_name = self.__trim_last_whitespaces(
                program_info[1].replace("\xa0", "")
            )
            if (datetime_start.hour < last_hour):
                datetime_start += timedelta(days=1)
                current_day += timedelta(days=1)

            last_hour = datetime_start.hour

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
    
    def __trim_last_whitespaces(self, string: str):
        spaces_count = 0
        for i in reversed(string):
            if (i != " "):
                break
            spaces_count += 1

        return string[0 : len(string) - spaces_count - 1]

    
    def __parse_time(self, time, current_day) -> datetime:
        day = time.replace("\xa0", "").split(":") #\n            20:00

        return current_day.replace(
            hour=int(day[0]),
            minute=int(day[1]),
            second=0,
            tzinfo=self.__response_time_zone
        )


if (__name__=="__main__"):
    options = read_command_line_options()
    parser = KonTvParser(options.parser_options)
    run_parser_out_to_csv(parser, options.save_options)