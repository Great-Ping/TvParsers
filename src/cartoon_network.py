import asyncio
import aiohttp
import json
from datetime import datetime, UTC, timedelta, timezone
from bs4 import BeautifulSoup

from shared.models import TvProgramData
from shared.models import TvParser
from shared.options import Options, ParserOptions, read_command_line_options
from shared.output import run_parser_out_to_csv
from shared.utils import fill_finish_date_by_next_start_date, get_node_text, is_none_or_empty


#Не парсит саму старицу с рассписанием, а сразу парсит ответы от фреймворка на php
#Из за чего появились ленивые параметры day_offset и days_limit,
#которые указывают смещение (относительно текущего дня) и количетсво дней которые необходимо запарсить
class CatoonNetworkParser(TvParser):
    options: ParserOptions
    #__channel_url = "https://www.tvyayinakisi.com/cartoon-network-yayin-akisi/"
    __source_url ="https://api.tvyayinakisi.com/new/index.php?lang=tr&show=channel&cSlug=cartoon-network"
    __channel_name = "Cartoon Network"
    __channel_logo_url = None
    __response_time_zone = timezone(timedelta(hours=3))


    async def parse_async(self) -> list[TvProgramData]:
        headers = {
            "Accept":"application/json, text/javascript, */*; q=0.01",
            "Origin":"https://www.tvyayinakisi.com",
            "Referer":"https://www.tvyayinakisi.com/"
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(self.__source_url, headers=headers) as resp:
                json = await resp.json()
                return self.__parse_json(json)

    def __parse_json(self, input: str):
        parsed_programs = []
        
        for program in input["content"]:
            parsed_programs.append(
                self.__parse_program(program)
            )

        return parsed_programs

    def __parse_program(self, program):
        return TvProgramData(
            self.__parse_time(program["brod_start"]),
            self.__parse_time(program["brod_end"]),
            self.__channel_name,
            program["name"],
            None,
            None,
            False
        )

    def __parse_time(self, time_str):
        return datetime.fromisoformat(time_str).replace(
            tzinfo=self.__response_time_zone
        )


if (__name__=="__main__"):
    options = read_command_line_options()
    parser = CatoonNetworkParser(options.parser_options)
    run_parser_out_to_csv(parser, options.save_options)