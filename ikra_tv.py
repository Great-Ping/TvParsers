import asyncio
import aiohttp
from datetime import datetime, UTC, timedelta, timezone
from bs4 import BeautifulSoup

from shared.models import TvParser, TvProgramData
from shared.options import SaveOptions
from shared.output import run_parser_out_to_csv
from shared.utils import fill_finish_date_by_next_start_date, get_monday_datetime

class IkraTvParser(TvParser):
    __day_urls = [
        "https://www.ikratv.com/yayin-akisi/pazartesi",
        "https://www.ikratv.com/yayin-akisi/sali",
        "https://www.ikratv.com/yayin-akisi/carsamba",
        "https://www.ikratv.com/yayin-akisi/persembe",
        "https://www.ikratv.com/yayin-akisi/cuma",
        "https://www.ikratv.com/yayin-akisi/cumartesi",
        "https://www.ikratv.com/yayin-akisi/pazar"
    ]

    __channel_name = "İkra TV"
    #__channel_logo_url = "https://www.ikratv.com/templates/default/images/logo.png"
    __channel_logo_url = None
    __time_zone_delta = timedelta(hours=3)

    def __parse_html(self, html_input: str, current_day: datetime):
        html = BeautifulSoup(html_input, 'html.parser')
        programs = html.find("div", {"class": "streaming"})
        parsed_programs = []

        for program_info in programs.find_all("div", {"class": "info"}):
            time = program_info.span.contents[0].split(".")
            hours = int(time[0])
            minutes = int(time[1])
            show_name = program_info.strong.contents[0]
            
            datetime_start = current_day.replace(
                hour=hours,
                minute=minutes,
                second=0
            )
            
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
    
    async def parse_async(self) -> list[TvProgramData]:
        programs = []

        tz = timezone(self.__time_zone_delta)
        current_day = get_monday_datetime(tz)

        async with aiohttp.ClientSession() as session:
            for url in self.__day_urls:
                async with session.get(url) as resp:
                    html = await resp.text()
                    programs.extend(
                        self.__parse_html(html, current_day)
                    )
                    current_day += timedelta(days=1)

        fill_finish_date_by_next_start_date(programs)        

        return programs

if (__name__=="__main__"):
    parser = IkraTvParser()
    run_parser_out_to_csv(parser, SaveOptions("ikra_tv.csv"))