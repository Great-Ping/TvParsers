import asyncio
import aiohttp
from datetime import datetime, UTC, timedelta, timezone
from bs4 import BeautifulSoup

from shared.models import TvParser, TvProgramData
from shared.options import ParserOptions, SaveOptions, read_command_line_options
from shared.output import run_parser_out_to_csv
from shared.utils import fill_finish_date_by_next_start_date, get_monday_datetime

class MeltemTvParser(TvParser):
    __source_url = "https://www.meltemtv.com.tr/yayin-akisi"
    __channel_name = "Meltem TV"
    #__channel_logo_url = "https://i.hizliresim.com/n9otvqm.png"
    __channel_logo_url = None
    __response_time_zone = timezone(timedelta(hours=3))

    def __init__(self, options: ParserOptions) -> None:
        super().__init__(options)

    def __parse_day_programs(self, stream_list, current_day):
        day_programs = []
        stream_index = 0
        for stream_info in stream_list.find_all("div", {"class": "row"}):
            hours = int(stream_info.label.strong.contents[0].replace(":", ""))
            minutes = int(stream_info.label.contents[1])
            show_name = stream_info.span.i.contents[0]
            
            datetime_start = current_day.replace(
                hour=hours,
                minute=minutes,
                second=0,
                tzinfo=self.__response_time_zone
            )
            
            day_programs.append(TvProgramData(
                datetime_start,
                None,
                self.__channel_name,
                show_name,
                self.__channel_logo_url,
                None,
                False
            ))
            stream_index += 1

        return day_programs

    def __parse_html(self, html_input: str):
        
        html = BeautifulSoup(html_input, 'html.parser')
        stream_lists = html.find_all("div", {"class": "streamList"})
        parsed_programs = []

        current_day = get_monday_datetime(self.__response_time_zone)

        for stream_list in stream_lists:
            day_streams = self.__parse_day_programs(stream_list, current_day)
            parsed_programs.extend(day_streams)
            current_day += timedelta(days=1)

        fill_finish_date_by_next_start_date(parsed_programs)        

        return parsed_programs

    async def parse_async(self) -> list[TvProgramData]:
        async with aiohttp.ClientSession() as session:
            async with session.get(self.__source_url) as resp:
                html_text = await resp.text()
                return self.__parse_html(html_text)

if (__name__=="__main__"):
    options = read_command_line_options()
    parser = MeltemTvParser(options.parser_options)
    run_parser_out_to_csv(parser, options.save_options)