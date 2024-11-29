
import asyncio
import aiohttp
from datetime import datetime, UTC, timedelta, timezone
from bs4 import BeautifulSoup

from shared.options import SaveOptions, read_command_line_options
from shared.models import TvParser, TvProgramData
from shared.output import run_parser_out_to_csv
from shared.utils import fill_finish_date_by_next_start_date, get_monday_datetime, get_node_text

class BeyazTvParser(TvParser):
    #__channel_url = "https://beyaztv.com.tr/yayin-akisi" 
    __channel_name = "Beyaz TV"
    __channel_logo_url = None
    __response_time_zone = timezone(timedelta(hours=3))
    __day_urls = [
        "https://beyaztv.com.tr/yayin-akisi/pazartesi/",
		"https://beyaztv.com.tr/yayin-akisi/salı/",
		"https://beyaztv.com.tr/yayin-akisi/carsamba/",
		"https://beyaztv.com.tr/yayin-akisi/persembe/",
		"https://beyaztv.com.tr/yayin-akisi/cuma/",
		"https://beyaztv.com.tr/yayin-akisi/cumartesi/",
		"https://beyaztv.com.tr/yayin-akisi/pazar/",
    ]

    async def parse_async(self) -> list[TvProgramData]:
        async with aiohttp.ClientSession() as session:
            tasks = []
            
            http_urls = self.__day_urls
            
            current_day = get_monday_datetime(self.__response_time_zone)
            for url in http_urls: 
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
            
            return result

    async def parse_day_async(self, session, http_url, current_day) -> (datetime, list[TvProgramData]):
        async with session.get(http_url) as resp: 
            return (current_day, self.parse_day_html(await resp.text(), current_day))

    def parse_day_html(self, html_text:str, current_day:datetime):
        html = BeautifulSoup(html_text, 'html.parser')
        parsed_programs = []

        programs = html.find("tbody").find_all("tr")
        prev_hour = 0

        for program in programs:
            data = program.find_all("td", recursive=False)
            time = data[0].next.split(":")

            hours = int(time[0])
            minutes = int(time[1])

            program_name = get_node_text(data[2])

            if (prev_hour > hours):
                current_day += timedelta(days=1)
            prev_hour = hours

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

    
    def get_day_urls(self, html_text) -> list[str]:
        html = BeautifulSoup(html_text, 'html.parser')
        days_list = html.find("ul", {"class": "days-list"})
        a_tags = days_list.find_all("a")

        return [a_tag.attrs["href"] for a_tag in a_tags]

    
if (__name__=="__main__"):
    options = read_command_line_options()
    parser = BeyazTvParser(options.parser_options)
    run_parser_out_to_csv(parser, options.save_options)