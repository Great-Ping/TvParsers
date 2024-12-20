import asyncio
import aiohttp
import json
from datetime import datetime, UTC, timedelta, timezone
from bs4 import BeautifulSoup

from shared.models import TvProgramData
from shared.models import TvParser
from shared.options import Options, ParserOptions, SaveOptions, read_command_line_options
from shared.output import run_parser_out_to_csv
from shared.utils import fill_finish_date_by_next_start_date, is_none_or_empty


#Не парсит саму старицу с рассписанием, а сразу парсит ответы от фреймворка на php
#Из за чего появились ленивые параметры day_offset и days_limit,
#которые указывают смещение (относительно текущего дня) и количетсво дней которые необходимо запарсить
class DostTvParser(TvParser):
    options: ParserOptions
    #__channel_url = "https://dosttv.com/yayin-akisi/"
    __source_url = "https://dosttv.com/wp-admin/admin-ajax.php"
    __channel_name = "Dost TV"
    #__channel_logo_url = "https://dosttv.com/wp-content/uploads/2022/02/dost_logo.png"
    __channel_logo_url = None
    __response_time_zone = timezone(timedelta(hours=3))
    __form_data = "action=extvs_get_schedule_simple&param_shortcode=%7B%22style%22%3A%222%22%2C%22fullcontent_in%22%3A%22collapse%22%2C%22show_image%22%3A%22show%22%2C%22channel%22%3A%22Dost+TV%22%2C%22slidesshow%22%3A%22%22%2C%22slidesscroll%22%3A%22%22%2C%22start_on%22%3A%22%22%2C%22before_today%22%3A%22%22%2C%22after_today%22%3A%227%22%2C%22order%22%3A%22DESC%22%2C%22orderby%22%3A%22date%22%2C%22meta_key%22%3A%22%22%2C%22meta_value%22%3A%22%22%2C%22order_channel%22%3A%22yes%22%2C%22class%22%3A%22%22%2C%22ID%22%3A%22ex-8331%22%7D&chanel=Dost+TV&date="

    def __init__(self, options: ParserOptions):
        super().__init__(options)

    async def parse_async(self) -> list[TvProgramData]:
        parsed_programs = []

        async with aiohttp.ClientSession() as session:
            headers = {
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
            }

            current_day, finish_day = self.__prepare_days()

            while current_day <= finish_day:
                tz_unix = int((current_day - datetime(1970,1,1, tzinfo=UTC)).total_seconds())
                data = self.__form_data + str(tz_unix)
                async with session.post(self.__source_url, headers=headers, data=data) as resp:
                    resp_text = await resp.text()
                    resp_json = json.loads(resp_text)

                    parsed_programs.extend(
                        self.__parse_html(resp_json["html"], current_day)
                    )

                current_day += timedelta(days=1)
            
        fill_finish_date_by_next_start_date(parsed_programs)
        return parsed_programs

    def __parse_html(self, html_input: str, current_day: datetime):
        
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
                tzinfo=self.__response_time_zone,
                second=0
            )

            program_name = content.h3.next
            parsed_description = None

            if (description is not None):
                parsed_description = self.__get_node_text(description)

            parsed_programs.append(TvProgramData(
                datetime_start,
                None,
                self.__channel_name,
                program_name,
                self.__channel_logo_url,
                parsed_description,
                False
            ))

        return parsed_programs

    def __prepare_days(self) -> tuple[datetime, datetime]:
        current_day: datetime
        finish_day: datetime 
        if (self.options.start_date is not None):
            current_day = self.options.start_date
        else:
            current_day = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)
        
        if (self.options.finish_date is not None):
            finish_day = self.options.finish_date
        else:
            finish_day = current_day + timedelta(days=7)

        return (current_day, finish_day)

    
    def __get_node_text(self, node):
        if (isinstance(node, str)):
            return node

        stack = [*node.children]
        result = ""

        while(len(stack) > 0):
            node = stack.pop(0)
        
            if (isinstance(node, str)):
                if (is_none_or_empty(node)):
                    continue
                result += node
            else:
                if (node.name == "p" and len(result) > 0):
                    result += "\n"
                for index, child in enumerate(node.children):
                    stack.insert(index, child)

        return result

 



if (__name__=="__main__"):
    options = read_command_line_options()
    parser = DostTvParser(options.parser_options)
    run_parser_out_to_csv(parser, options.save_options)