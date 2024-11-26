import asyncio
import aiohttp
from typing import Union
from datetime import datetime, UTC, timedelta, timezone
from bs4 import BeautifulSoup

from shared.models import TvParser, TvProgramData
from shared.options import SaveOptions
from shared.output import run_parser_out_to_csv
from shared.utils import fill_finish_date_by_next_start_date, get_monday_datetime

#Особенность, для определения временной зоны используется наивный алгоритм
#Когда часы текущей передачи < предыдущей, значит наступил новый день
class Trt1Parser(TvParser):
    __source_url = "https://www.trt1.com.tr/yayin-akisi"
    __channel_name = "TRT 1"
    #__channel_logo_url = "https://www.semerkandtv.com.tr/Content/img/logo.png"
    __channel_logo_url = None
    __response_time_zone = timezone(timedelta(hours=3))

    target_day: Union[datetime, None]
    current_day: datetime

    def __init__(
            self,
            target_day: Union[datetime, None] = None
        ) -> None:
        #день отсчёта, если не указан то будут включены и прошедшие телепередачи
        self.target_day = target_day
        self.current_day = get_monday_datetime(self.__response_time_zone)
        self.__previous_hour = 0

    def __parse_day_programs(self, current_day_programs):
        parsed_programs = []
        stream_index = 0
        for program_info in current_day_programs.ul.find_all("li", recursive=False):
            time = program_info.time.span.a.next.split(".")

            hours = int(time[0])
            minutes = int(time[1])

            if (self.__previous_hour > hours):
                self.current_day += timedelta(days=1)

            self.__previous_hour = hours
            
            show_name = program_info.find("h2", {"class": "title"}).a.next
            datetime_start = self.current_day.replace(
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
        programs = html.find_all("div", {"role": "tabpanel"})
        parsed_programs = []

        for current_day_programs in programs:
            self.current_day
            day_streams = self.__parse_day_programs(current_day_programs)
            parsed_programs.extend(
                day_streams
            )

        fill_finish_date_by_next_start_date(parsed_programs)        

        return parsed_programs

    async def parse_async(self) -> list[TvProgramData]:
        async with aiohttp.ClientSession() as session:
            async with session.get(self.__source_url) as resp:
                html_text = await resp.text()
                return self.__parse_html(html_text)

if (__name__=="__main__"):
    parser = Trt1Parser()
    run_parser_out_to_csv(parser, SaveOptions("trt1.csv"))