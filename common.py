import asyncio
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
        datetime_start: str, 
        datetime_finish: str,
        channel: str,
        title: str,
        channel_logo_url: str,
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


def format_date(datetime):
    return datetime.strftime("%Y-%m-%dT%H:%M:%S+00:00")

def escape(input: str):
    return input

async def out_to_csv_async(tvPrograms: List[TvProgramData], config: Config):
    async with async_open(config.output_path, "w+") as asyncStream:
        for tvProgram in tvPrograms:
            await asyncStream.write(
                f"\"{escape(tvProgram.datetime_start)}\"" 
                + f";\"{escape(tvProgram.datetime_finish)}\""
                + f";\"{escape(tvProgram.channel)}\""
                + f";\"{escape(tvProgram.title)}\""
                + f";\"{escape(tvProgram.channel_logo_url)}\""
                + f";\"{escape(tvProgram.description)}\""
                + f";\"{tvProgram.available_archive}\""
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