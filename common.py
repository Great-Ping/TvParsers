import asyncio
from datetime import datetime, timezone, timedelta
from typing import *
from aiofile import async_open
from abc import ABC, abstractmethod, abstractproperty

class Config:
    def __init__(
        self,
        output_path
    ):
        self.output_path = output_path

class TvProgramData:
    def __init__(
        self, 
        datetime_start: datetime, 
        datetime_finish: [datetime|None],
        channel: str,
        title: str,
        channel_logo_url: [str|None],
        description: [str|None],
        available_archive: bool
    ):
        #формате YYYY-mm-ddThh:mm:ss+tz:tz (пример - 2024-07-22T16:27:01+00:00)
        self.datetime_start = datetime_start
        #формате YYYY-mm-ddThh:mm:ss+tz:tz (пример - 2024-07-22T16:27:01+00:00)
        self.datetime_finish = datetime_finish
        #channel - строка - название телеканала
        self.channel = channel
        #строка - название телепередачи
        self.title = title

        self.channel_logo_url = channel_logo_url
        #строка - URL на изображение телеканала
        self.description = description
        #число 1 или 0 - доступность архива
        self.available_archive = available_archive

class TvParser(ABC):
    @abstractmethod
    async def parse_async(self) ->  list[TvProgramData]:
        pass

def get_monday_datetime(timezone):
    now = datetime.now(timezone)
    now -= timedelta(days=now.weekday())
    return now

def escape(input: str):
    if (input is None):
        return "\"\""

    return f"\"{input}\""

def format_date(date: [datetime|None]):
    if (date is None):
        return ""

    return date.isoformat("T", "seconds")

def fill_finish_date_by_next_start_date(tv_programs: List[TvProgramData]):
    for i in range(1, len(tv_programs)):
        tv_programs[i-1].datetime_finish = tv_programs[i].datetime_start


async def out_to_csv_async(tvPrograms: List[TvProgramData], config: Config):

    async with async_open(config.output_path, "w+") as asyncStream:
        await asyncStream.write("\"datetime_start\";\"datetime_finish\";\"channel\";\"title\";\"channel_logo_url\";\"description\";\"available_archive\"\n")


        for tvProgram in tvPrograms:
            await asyncStream.write(
                f"{escape(format_date(tvProgram.datetime_start))}" 
                + f";{escape(format_date(tvProgram.datetime_finish))}"
                + f";{escape(tvProgram.channel)}"
                + f";{escape(tvProgram.title)}"
                + f";{escape(tvProgram.channel_logo_url)}"
                + f";{escape(tvProgram.description)}"
                + f";{str(int(tvProgram.available_archive))}"
                + "\n"
            )

async def run_parser_out_to_csv_async(parser: TvParser, config: Config):
    parsedData = await parser.parse_async()
    await out_to_csv_async(parsedData, config)

def run_parser_out_to_csv(parser: TvParser, config: Config):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        run_parser_out_to_csv_async(parser, config)
    )