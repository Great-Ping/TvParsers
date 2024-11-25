import asyncio
import aiohttp

from common import *

class MeltemTvParser(TvParser):
    sourceUrl = "https://www.meltemtv.com.tr/yayin-akisi"


    async def parse_async(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.sourceUrl) as resp:
                print(resp.status)
                print(await resp.text())


        return [
            TvProgramData(
                "datetime_start: str,     ",        
                "datetime_finish: str,    ",      
                "channel: str,",
                "title: str,              ",  
                "channel_logo_url: str,   ",      
                "description: [str|None], ",      
                "available_archive: bool  "     
            )
        ]

if (__name__=="__main__"):
    parser = MeltemTvParser()
    run_parser_out_to_csv(parser, Config("meltem_tv.csv"))