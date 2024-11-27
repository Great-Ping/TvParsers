import asyncio
import aiohttp
from datetime import datetime, UTC, timedelta, timezone
from bs4 import BeautifulSoup
from py_mini_racer import MiniRacer

from shared.options import SaveOptions, read_command_line_options
from shared.models import TvParser, TvProgramData
from shared.output import run_parser_out_to_csv



class TrtCocukParser(TvParser):
    __source_url = "https://www.trtcocuk.net.tr/yayin-akisi/" 
    __channel_name = "TRT ÇOCUK"
    __channel_logo_url = None

    async def parse_async(self) -> list[TvProgramData]:
        async with aiohttp.ClientSession() as session:
            async with session.get(self.__source_url) as resp:
                result = self.parse_day_html(await resp.text())
                return result

    def parse_day_html(self, html_text:str):
        html = BeautifulSoup(html_text, 'html.parser')
        parsed_programs = []
        
        programs = html.body.find("script", recursive=False)

        js_interop = MiniRacer()
        obj = js_interop.eval(programs.next.replace("window.__NUXT__=", "result=")+" result")

        program_days = obj["data"][0]["data"]["week"]
        for day in program_days:
            for program in day["epg"]:
                parsed_programs.append(
                    self.parse_program(program)
                )
        
        js_interop.close()
        return parsed_programs
    
    def parse_program(self, program):
        return TvProgramData(
            self.parse_time(program["startTime"]),
            self.parse_time(program["endTime"]),
            self.__channel_name,
            program["title"],
            None,
            None,
            0
        )


    @staticmethod
    def parse_time(time_str: str) -> datetime:
        return datetime.fromisoformat(time_str)
    
if (__name__=="__main__"):
    options = read_command_line_options()
    parser = TrtCocukParser(options.parser_options)
    run_parser_out_to_csv(parser, options.save_options)
