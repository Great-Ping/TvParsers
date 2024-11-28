
import asyncio
from typing import Tuple
import aiohttp
from datetime import datetime, UTC, timedelta, timezone
from bs4 import BeautifulSoup

from shared.options import SaveOptions, read_command_line_options
from shared.models import TvParser, TvProgramData
from shared.output import run_parser_out_to_csv
from shared.utils import fill_finish_date_by_next_start_date, get_monday_datetime, get_node_text, is_none_or_empty

class AksuTvParser(TvParser):
    #__channel_url = "https://beyaztv.com.tr/yayin-akisi" 
    __channel_name = "aksu tv"
    __channel_logo_url = None
    __response_time_zone = timezone(timedelta(hours=3))
    __day_urls = [
        "https://www.aksutv.com.tr/yayin-akisi/Pazartesi",
		"https://www.aksutv.com.tr/yayin-akisi/Sali",
		"https://www.aksutv.com.tr/yayin-akisi/Carsamba",
		"https://www.aksutv.com.tr/yayin-akisi/Persembe",
		"https://www.aksutv.com.tr/yayin-akisi/Cuma",
		"https://www.aksutv.com.tr/yayin-akisi/Cumartesi",
		"https://www.aksutv.com.tr/yayin-akisi/Pazar",
    ]

    async def parse_async(self) -> list[TvProgramData]:
        async with aiohttp.ClientSession() as session:
            tasks = []
            
            http_urls = self.__day_urls
            
            current_day = get_monday_datetime(self.__response_time_zone)
            
            for url in http_urls: 
                if (self.in_config_time_interval(current_day)):
                    tasks.append(
                        self.parse_day_async(session, url, current_day)
                    )
        
                current_day += timedelta(days=1)

            parsed_days_result = await asyncio.gather(*tasks)
            sorted_by_dates = sorted(parsed_days_result, key=lambda x: x[0])
            
            result = [ 
                program 
                for day in sorted_by_dates 
                    for program in day[1]
            ]            
        
            fill_finish_date_by_next_start_date(result)
            
            return list(filter(lambda x: x.title != None, result))

    async def parse_day_async(
        self, 
        session, 
        http_url, 
        current_day
    ) -> Tuple[datetime, list[TvProgramData]]:
        async with session.get(http_url) as resp: 
            return (
                current_day, 
                self.parse_day_html(await resp.text(), current_day)
            )

    def parse_day_html(self, html_text:str, current_day:datetime):
        html = BeautifulSoup(html_text, 'html.parser')
        parsed_programs = []

        container = html.body.find("div", {"class":"container"}, recursive=False)
        container = container.find_all("div", recursive=False)[1]

        programs = container.find_all("div", recursive=False)

        for program in programs:
            time = get_node_text(program.find("h1")).split(".")

            hours = int(time[0])
            minutes = int(time[1])

            program_name = self.__get_or_default_title_from_url(
                program.find("img").attrs["src"]
            )

            datetime_start = current_day.replace(
                hour=hours,
                minute=minutes,
                second=0,
                tzinfo=self.__response_time_zone
            )
            
            parsed_programs.append(TvProgramData(
                datetime_start,
                None,
                self.__channel_name,
                program_name,
                self.__channel_logo_url,
                None,
                False
            ))

        return parsed_programs

    def __get_or_default_title_from_url(self, url:str)->str:
        parts = url.split("programlar")
        
        if len(parts) != 2:
            return None

        right_part = parts[1]
        name = ""
        for i in right_part:
            if (i == "(" or i == "-"):
                break
            name += i

        if (is_none_or_empty(name)):
            return None
        
        return name

        


if (__name__=="__main__"):
    options = read_command_line_options()
    parser = AksuTvParser(options.parser_options)
    run_parser_out_to_csv(parser, options.save_options)