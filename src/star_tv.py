
import asyncio
import aiohttp
from datetime import datetime, UTC, timedelta, timezone
from bs4 import BeautifulSoup

from shared.options import SaveOptions, read_command_line_options
from shared.models import TvParser, TvProgramData
from shared.output import run_parser_out_to_csv
from shared.utils import fill_finish_date_by_next_start_date, get_monday_datetime, is_none_or_empty

class StartTvParser(TvParser):
    #__channel_url ="https://www.startv.com.tr/yayin-akisi"
    #есть параметр запроса date, который не используется
    __source_url = "https://www.startv.com.tr/api/schedule" 
    __channel_name = "STAR TV"
    __channel_logo_url = None
    __response_time_zone = timezone(timedelta(hours=3))

    async def parse_async(self) -> list[TvProgramData]:
        async with aiohttp.ClientSession() as session:
            async with session.get(self.__source_url) as resp:
                json = await resp.json()
                return self.__parse_json(json)
    
    def __parse_json(self, programs:list[dict]):
        parsed_programs = []

        for program in programs:
            parsed_programs.append(
                self.parse_program(program)
            )

        return parsed_programs

    def parse_program(self, program: dict):
        end_time_str = program["endTime"]
        start_time_str = program["startTime"]
        program_name = program["title"]

        description = program["description"]
        content = program["content"]
        
        if (is_none_or_empty(description) and content != None):
            description = content["plain_summary"]

        datetime_finish = self.parse_time(end_time_str)
        datetime_start = self.parse_time(start_time_str)


        return TvProgramData(
            datetime_start,
            datetime_finish,
            self.__channel_name,
            program_name,
            None,
            description,
            False
        )
    
    @staticmethod
    def parse_time(time_str: str) -> datetime:
        return datetime.fromisoformat(time_str)
    
if (__name__=="__main__"):
    options = read_command_line_options()
    parser = StartTvParser(options.parser_options)
    run_parser_out_to_csv(parser, options.save_options)