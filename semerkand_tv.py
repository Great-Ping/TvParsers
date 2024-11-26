import asyncio
import aiohttp
from datetime import datetime, UTC, timedelta, timezone
from bs4 import BeautifulSoup

from shared.options import SaveOptions
from shared.models import TvParser, TvProgramData
from shared.output import run_parser_out_to_csv
from shared.utils import fill_finish_date_by_next_start_date, get_monday_datetime

class SemerkandTvParser(TvParser):
    __source_url = "https://www.semerkandtv.com.tr/yayin-akisi"
    __channel_name = "Semerkand TV"
    #__channel_logo_url = "https://www.semerkandtv.com.tr/Content/img/logo.png"
    __channel_logo_url = None
    __time_zone_delta = timedelta(hours=3)

    def __parse_day_programs(self, current_day_programs, current_day):
        parsed_programs = []
        stream_index = 0
        for program_info in current_day_programs.find_all("div", {"class": "item"}):
            program_info = program_info.find_all("span")
            
            time = program_info[1].contents[0].split(":")

            hours = int(time[0])
            minutes = int(time[1])

            show_name = program_info[0].contents[0]
            
            datetime_start = current_day.replace(
                hour=hours,
                minute=minutes,
                second=0
            )
            
            parsed_programs.append(TvProgramData(
                datetime_start,
                None,
                self.__channel_name,
                show_name,
                self.__channel_logo_url,
                None,
                False
            ))
            stream_index += 1

        return parsed_programs

    def __parse_html(self, html_input: str):
        
        html = BeautifulSoup(html_input, 'html.parser')
        programs = html.find_all("div", {"class": "streaming"})
        parsed_programs = []

        tz = timezone(self.__time_zone_delta)
        current_day = get_monday_datetime(tz)

        for current_day_programs in programs:
            day_streams = self.__parse_day_programs(current_day_programs, current_day)
            parsed_programs.extend(day_streams)
            current_day += timedelta(days=1)

        fill_finish_date_by_next_start_date(parsed_programs)        

        return parsed_programs

    async def parse_async(self) -> list[TvProgramData]:
        async with aiohttp.ClientSession() as session:
            async with session.get(self.__source_url) as resp:
                html_text = await resp.text()
                return self.__parse_html(html_text)

if (__name__=="__main__"):
    parser = SemerkandTvParser()
    run_parser_out_to_csv(parser, SaveOptions("semerkand_tv.csv"))