import asyncio
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
class Trt2Parser(TvParser):
    __source_url = "https://www.trt.net.tr/yayin-akisi"
    __channel_name = "trt 2"
    __channel_logo_url = None
    __response_time_zone = timezone(timedelta(hours=3))
    __remove_last = True

    async def parse_async(self) -> list[TvProgramData]:
        async with aiohttp.ClientSession() as session:
            async with session.get(self.__source_url) as resp:
                html_text = await resp.text()
                return self.__parse_html(html_text)

    def __parse_html(self, html_input: str):
        html = BeautifulSoup(html_input, 'html.parser')
        program_days = html.find_all("ul", {"class": "event-list"})
        channel_programs = self.__select_target_channel_tag(html, "TRT 2 Yayın Akışı")

        current_day = datetime.now(self.__response_time_zone)
        parsed_programs = self.__parse_day_programs(channel_programs, current_day)

        fill_finish_date_by_next_start_date(parsed_programs, self.__remove_last)        
        return parsed_programs
    
    def __select_target_channel_tag(self, html, target_channel_name):
        all_channels = html.find("div", {"class": "stream-conteiner"})
        channels_cards = all_channels.find_all("div", recursive=False)
        for card in channels_cards:
            card = card.div.div
            channel_name = card.find("h2", {"class":"card-texts"}).next
            if (target_channel_name in channel_name):
                return card

    def __parse_day_programs(self, current_day_programs, current_day):
        parsed_programs = []
        last_hour = 0
        for program_info in current_day_programs.find_all("div", recursive=False):
            datetime_start = self.__parse_time(
                program_info.find("span", {"class": "livestream-time"}).next,
                current_day
            )
            show_name = program_info.find("span", {"class": "livestream-title"}).next

            if (datetime_start.hour < last_hour):
                datetime_start += timedelta(days=1)
                current_day += timedelta(days=1)
                
            last_hour = datetime_start.hour

            parsed_programs.append(TvProgramData(
                datetime_start,
                None,
                self.__channel_name,
                show_name,
                self.__channel_logo_url,
                None,
                False
            ))
            
        return parsed_programs
    
    def __parse_time(self, time, current_day) -> datetime:
        day = time.split(".") #20.00
        return current_day.replace(
            hour=int(day[0]),
            minute=int(day[1]),
            second=0,
            tzinfo=self.__response_time_zone
        )


if (__name__=="__main__"):
    options = read_command_line_options()
    parser = Trt2Parser(options.parser_options)
    run_parser_out_to_csv(parser, options.save_options)
