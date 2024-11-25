import asyncio
import aiohttp
from datetime import datetime, UTC, timedelta, timezone
from bs4 import BeautifulSoup

from common import *

class MeltemTvParser(TvParser):
    source_url = "https://www.meltemtv.com.tr/yayin-akisi"
    channel_name = "Meltem TV"
    #channel_logo_url = "https://i.hizliresim.com/n9otvqm.png"
    channel_logo_url = None
    time_zone_delta = timedelta(hours=3)

    def parse_day_programs(self, stream_list, current_day):
        day_programs = []
        stream_index = 0
        for stream_info in stream_list.find_all("div", {"class": "row"}):
            hours = int(stream_info.label.strong.contents[0].replace(":", ""))
            minutes = int(stream_info.label.contents[1])
            show_name = stream_info.span.i.contents[0]
            
            datetime_start = current_day.replace(
                hour=hours,
                minute=minutes,
                second=0
            )
            
            day_programs.append(TvProgramData(
                datetime_start,
                None,
                self.channel_name,
                show_name,
                self.channel_logo_url,
                None,
                False
            ))
            stream_index += 1

        return day_programs

    def parse_html(self, html_input: str):
        
        html = BeautifulSoup(html_input, 'html.parser')
        stream_lists = html.find_all("div", {"class": "streamList"})
        parsed_programs = []

        tz = timezone(self.time_zone_delta)
        current_day = datetime.now(tz)

        for stream_list in stream_lists:
            day_streams = self.parse_day_programs(stream_list, current_day)
            parsed_programs.extend(day_streams)
            current_day += timedelta(days=1)

        fill_finish_date_by_next_start_date(parsed_programs)        

        return parsed_programs

    async def parse_async(self) -> List[TvProgramData]:
        async with aiohttp.ClientSession() as session:
            async with session.get(self.source_url) as resp:
                html_text = await resp.text()
                return self.parse_html(html_text)

if (__name__=="__main__"):
    parser = MeltemTvParser()
    run_parser_out_to_csv(parser, Config("meltem_tv.csv"))