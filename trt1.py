import asyncio
import aiohttp
from datetime import datetime, UTC, timedelta, timezone
from bs4 import BeautifulSoup

from common import *

class Trt1Parser(TvParser):
    source_url = "https://www.trt1.com.tr/yayin-akisi"
    channel_name = "TRT 1"
    #channel_logo_url = "https://www.semerkandtv.com.tr/Content/img/logo.png"
    channel_logo_url = None
    time_zone_delta = timedelta(hours=3)

    def __init__(
            self,
            target_day: Union[datetime, None] = None
        ) -> None:
        #день отсчёта, если не указан то будут включены и прошедшие телепередачи
        self.target_day = target_day


    def parse_day_programs(self, current_day_programs, current_day):
        parsed_programs = []
        stream_index = 0
        for program_info in current_day_programs.ul.find_all("li", recursive=False):
            time = program_info.time.span.a.next.split(".")

            hours = int(time[0])
            minutes = int(time[1])

            show_name = program_info.find("h2", {"class": "title"}).a.next
            
            datetime_start = current_day.replace(
                hour=hours,
                minute=minutes,
                second=0
            )
            
            parsed_programs.append(TvProgramData(
                datetime_start,
                None,
                self.channel_name,
                show_name,
                self.channel_logo_url,
                None,
                False
            ))
            stream_index += 1

        return parsed_programs

    def parse_html(self, html_input: str):
        
        html = BeautifulSoup(html_input, 'html.parser')
        programs = html.find_all("div", {"role": "tabpanel"})
        parsed_programs = []

        tz = timezone(self.time_zone_delta)
        current_day = get_monday_datetime(tz)

        for current_day_programs in programs:
            if (self.target_day is None or current_day >= self.target_day):
                day_streams = self.parse_day_programs(current_day_programs, current_day)
                parsed_programs.extend(
                    sorted(day_streams, key=lambda x: x.datetime_start)
                )

            current_day += timedelta(days=1)

        fill_finish_date_by_next_start_date(parsed_programs)        

        return parsed_programs

    async def parse_async(self) -> List[TvProgramData]:
        async with aiohttp.ClientSession() as session:
            async with session.get(self.source_url) as resp:
                html_text = await resp.text()
                return self.parse_html(html_text)

if (__name__=="__main__"):
    parser = Trt1Parser()
    run_parser_out_to_csv(parser, Config("trt1.csv"))