import asyncio
import json
import aiohttp
from typing import Union
from datetime import datetime, UTC, timedelta, timezone
from bs4 import BeautifulSoup

from shared.models import TvParser, TvProgramData
from shared.options import SaveOptions, read_command_line_options
from shared.output import run_parser_out_to_csv
from shared.utils import fill_finish_date_by_next_start_date, is_none_or_empty

#Особенность, для определения временной зоны используется наивный алгоритм
#Когда часы текущей передачи < предыдущей, значит наступил новый день
class TrtSportYildiziParser(TvParser):
    __source_url = "https://www.trtspor.com.tr/yayin-akisi/trt-spor-yildiz"
    __channel_name = "trt spor yıldız"
    __channel_id = 129464
    __channel_logo_url = None
    __response_time_zone = timezone(timedelta(hours=3))

    async def parse_async(self) -> list[TvProgramData]:
        async with aiohttp.ClientSession() as session:
            async with session.get(self.__source_url) as resp:
                html_text = await resp.text()
                return self.__parse_html(html_text)

    def __parse_html(self, html_input: str):
        html = BeautifulSoup(html_input, 'html.parser')
        data_script = html.find("script", {"id": "__NEXT_DATA__"})

        parsed_programs = self.__parse_json(json.loads(data_script.text))
        return parsed_programs

    def __parse_json(self, data):
        parsed_programs = []
        stream_index = 0
        programs = self.__prepare_channel_programs(data)

        for program_info in programs:
            datetime_start = self.__parse_time(program_info["starttime"])
            datetime_finish = self.__parse_time(program_info["endtime"])
                                               
            show_name = program_info["title"]
            show_description = program_info["synopsis"].replace("''", "\"").replace("\n", " ")
            
            if (is_none_or_empty(show_description)):
                show_description = None

            parsed_programs.append(TvProgramData(
                datetime_start,
                datetime_finish,
                self.__channel_name,
                show_name,
                self.__channel_logo_url,
                show_description,
                    False
            ))
            stream_index += 1

        return parsed_programs
    
    def __prepare_channel_programs(self, data) -> dict[str, any]:
        rows = data["props"]["pageProps"]["data"]["rows"]
        epg = self.__find_epg(rows)
        result = []

        for day in epg:
            programs = self.__select_channel_programs(day, self.__channel_id)
            if (programs is None):
                continue    
            result.extend(programs)
        return result 
    
    @staticmethod
    def __select_channel_programs(epg_day, channel_id):
        for channel in epg_day["tvChannels"]:
            if (channel["id"] == channel_id):
                current = []
                if channel["current"] != {}:
                    current = [channel["current"]]
                return channel["past"] + current + channel["upcoming"]
        
    def __find_epg(self, rows):
        if (rows[4]["type"] == "detail-row"):
            return rows[4]["content"]["epg"]
        
        for row in rows:
            if row["type"] == "detail-row":
                return row["content"]["epg"]

        raise TypeError("Epg not found")

    def __parse_time(self, time) -> datetime:
        return datetime.fromisoformat(time)

if (__name__=="__main__"):
    options = read_command_line_options()
    parser = TrtSportYildiziParser(options.parser_options)
    run_parser_out_to_csv(parser, options.save_options)
