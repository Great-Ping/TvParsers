import asyncio
from datetime import datetime
import os
from typing import *
from aiofile import async_open

from .options import SaveOptions
from .models import TvParser, TvProgramData

def escape(input: str):
    if (input is None):
        return "\"\""

    input = input.replace("\"", "\"\"")
    return f"\"{input}\""

def __format_date(date: Union[datetime, None]):
    if (date is None):
        return ""

    return date.isoformat("T", "seconds")
    
def __to_csv_line(data:TvProgramData):
    return (f"{escape(__format_date(data.datetime_start))}" 
    + f";{escape(__format_date(data.datetime_finish))}"
    + f";{escape(data.channel)}"
    + f";{escape(data.title)}"
    + f";{escape(data.channel_logo_url)}"
    + f";{escape(data.description)}"
    + f";{str(int(data.available_archive))}"
    + "\n")

async def __out_to_csv_async(tvPrograms: list[TvProgramData], options: SaveOptions):
    os.makedirs(os.path.dirname(options.output_path), exist_ok=True)
    async with async_open(options.output_path, "w+") as asyncStream:
        await asyncStream.write("\"datetime_start\";\"datetime_finish\";\"channel\";\"title\";\"channel_logo_url\";\"description\";\"available_archive\"\n")

        for tvProgram in tvPrograms:
            await asyncStream.write(
                __to_csv_line(tvProgram)
            )

async def run_parser_out_to_csv_async(parser: TvParser, options: SaveOptions):
    parsedData = await parser.parse_async()
    await __out_to_csv_async(parsedData, options)

def run_parser_out_to_csv(parser: TvParser, options: SaveOptions):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        run_parser_out_to_csv_async(parser, options)
    )