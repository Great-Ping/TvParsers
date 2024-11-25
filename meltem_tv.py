import asyncio
import aiohttp
from datetime import datetime

from common import *
from bs4 import BeautifulSoup


class MeltemTvParser(TvParser):
    sourceUrl = "https://www.meltemtv.com.tr/yayin-akisi"

    def parse_day_streams(self, stream_list, current_day):
        for stream_info in stream_list.find_all("div", {"class": "row"}):
            print(stream_info)

    def parse_html(self, html_input: str):
        
        html = BeautifulSoup(html_input, 'html.parser')
        stream_lists = html.find_all("div", {"class": "streamList"})
        
        current_day = datetime.utcnow()

        for stream_list in stream_lists:
            self.parse_day_streams(stream_list, current_day)
            current_day = current_day.replace(day = current_day.day + 1)

        return []

    async def parse_async(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.sourceUrl) as resp:
                html_text = await resp.text()
                return self.parse_html(html_text)

        # return [
        #     TvProgramData(
        #         "datetime_start: str,     ",        
        #         "datetime_finish: str,    ",      
        #         "channel: str,",
        #         "title: str,              ",  
        #         "channel_logo_url: str,   ",      
        #         "description: [str|None], ",      
        #         "available_archive: bool  "     
        #     )
        # ]

if (__name__=="__main__"):
    parser = MeltemTvParser()
    run_parser_out_to_csv(parser, Config("meltem_tv.csv"))