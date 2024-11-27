import asyncio
import aiohttp
from datetime import datetime, UTC, timedelta, timezone
from bs4 import BeautifulSoup

from shared.models import TvParser, TvProgramData
from shared.options import SaveOptions, read_command_line_options
from shared.output import run_parser_out_to_csv
from shared.utils import fill_finish_date_by_next_start_date, get_monday_datetime, is_none_or_empty

#Особенность, для определения временной зоны используется наивный алгоритм
#Когда часы текущей передачи < предыдущей, значит наступил новый день
class Trt1Parser(TvParser):
    __source_url = "https://www.trt1.com.tr/yayin-akisi"
    __channel_name = "TRT 1"
    #__channel_logo_url = "https://www.semerkandtv.com.tr/Content/img/logo.png"
    __channel_logo_url = None
    __response_time_zone = timezone(timedelta(hours=3))

    async def parse_async(self) -> list[TvProgramData]:
        async with aiohttp.ClientSession() as session:
            async with session.get(self.__source_url) as resp:
                html_text = await resp.text()
                return self.__parse_html(html_text)

    def __parse_html(self, html_input: str):
        
        html = BeautifulSoup(html_input, 'html.parser')
        program_days = html.find_all("ul", {"class": "event-list"})
        parsed_programs = []

        for current_day_programs in program_days:
            parsed_programs.extend(
                self.__parse_day_programs(current_day_programs)
            )

        fill_finish_date_by_next_start_date(parsed_programs)        

        return parsed_programs

    def __parse_day_programs(self, current_day_programs):
        parsed_programs = []
        stream_index = 0
        for program_info in current_day_programs.find_all("li", recursive=False):
            datetime_start = self.__parse_time(program_info.time)
            show_name = program_info.find("h2", {"class": "title"}).a.next
            show_description = program_info.find("p", {"class": "desc"}).a.next
            if (is_none_or_empty(show_description)):
                show_description = None

            parsed_programs.append(TvProgramData(
                datetime_start,
                None,
                self.__channel_name,
                show_name,
                self.__channel_logo_url,
                show_description,
                False
            ))
            stream_index += 1

        return parsed_programs
    
    def __parse_time(self, time) -> datetime:
        date = time.attrs["datetime"] #27.11.2024
        day = time.find("a").next.split(".") #20:00
        return datetime.strptime(date, "%d.%m.%Y").replace(
            hour=int(day[0]),
            minute=int(day[1]),
            tzinfo=self.__response_time_zone
        )


if (__name__=="__main__"):
    options = read_command_line_options()
    parser = Trt1Parser(options.parser_options)
    run_parser_out_to_csv(parser, options.save_options)
