import asyncio
import aiohttp
import json
from datetime import datetime, UTC, timedelta, timezone
from bs4 import BeautifulSoup

from common import *

#Не парсит саму старицу с рассписанием, а сразу парсит ответы от фреймворка на php
#Из за чего появились ленивые параметры day_offset и days_limit,
#которые указывают смещение (относительно текущего дня) и количетсво дней которые необходимо запарсить
class SemerkandTvParser(TvParser):
    #channel_url = "https://dosttv.com/yayin-akisi/"
    source_url = "https://dosttv.com/wp-admin/admin-ajax.php"
    channel_name = "Dost TV"
    #channel_logo_url = "https://dosttv.com/wp-content/uploads/2022/02/dost_logo.png"
    channel_logo_url = None
    time_zone_delta = timedelta(hours=3)
    form_data = "action=extvs_get_schedule_simple&param_shortcode=%7B%22style%22%3A%222%22%2C%22fullcontent_in%22%3A%22collapse%22%2C%22show_image%22%3A%22show%22%2C%22channel%22%3A%22Dost+TV%22%2C%22slidesshow%22%3A%22%22%2C%22slidesscroll%22%3A%22%22%2C%22start_on%22%3A%22%22%2C%22before_today%22%3A%22%22%2C%22after_today%22%3A%227%22%2C%22order%22%3A%22DESC%22%2C%22orderby%22%3A%22date%22%2C%22meta_key%22%3A%22%22%2C%22meta_value%22%3A%22%22%2C%22order_channel%22%3A%22yes%22%2C%22class%22%3A%22%22%2C%22ID%22%3A%22ex-8331%22%7D&chanel=Dost+TV&date="

    def __init__(self, day_offset, days_limit):
        self.day_offset = day_offset
        self.days_limit = days_limit

    def get_node_text(self, node):
        stack = [node]
        result = ""
        while(len(stack) > 0):
            node = stack.pop()
            if (isinstance(node, str)):
                result += node
            else:
                for index, child in enumerate(node.children):
                    stack.insert(index, child)

        return result

    def parse_description(self, html_input):
        result = ""
        
        for paragraph in html_input.children:
            result += self.get_node_text(paragraph)

        return result


    def parse_html(self, html_input: str, current_day: datetime):
        
        html = BeautifulSoup(html_input, 'html.parser')
        programs = html.find("tbody").find_all("tr")
        parsed_programs = []

        for program in programs:
            time_tag = program.find("td", {"class":"extvs-table1-time"})
            time = time_tag.span.next.split(":")

            content = program.find("figure")
            description = content.find("div", {"class": "extvs-collap-ct"})

            hours = int(time[0])
            minutes = int(time[1])
            datetime_start = current_day.replace(
                hour=hours,
                minute=minutes,
                second=0
            )

            program_name = content.h3.next
            parsed_description = None

            if (description is not None):
                parsed_description = self.parse_description(description)

            parsed_programs.append(TvProgramData(
                datetime_start,
                None,
                self.channel_name,
                program_name,
                self.channel_logo_url,
                parsed_description,
                False
            ))

        return parsed_programs
    


    async def parse_async(self) -> List[TvProgramData]:
        parsed_programs = []

        async with aiohttp.ClientSession() as session:
            headers = {
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
            }

            tz = timezone(self.time_zone_delta)
            current_day = datetime.now(tz).replace(hour=0, minute=0, second=0, microsecond=0)
            current_day += timedelta(days=self.day_offset)


            for i in range(0, self.days_limit):
                tz_unix = int((current_day - datetime(1970,1,1, tzinfo=tz)).total_seconds())
                data = self.form_data + str(tz_unix)
                async with session.post(self.source_url, headers=headers, data=data) as resp:

                    resp_text = await resp.text()
                    resp_json = json.loads(resp_text)

                    parsed_programs.extend(
                        self.parse_html(resp_json["html"], current_day)
                    )

            current_day += timedelta(days=1)
            
        fill_finish_date_by_next_start_date(parsed_programs)
        return parsed_programs

if (__name__=="__main__"):
    parser = SemerkandTvParser(day_offset=0, days_limit=7)
    run_parser_out_to_csv(parser, Config("dost_tv.csv"))