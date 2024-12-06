import asyncio
from datetime import datetime
import os
from typing import *
from aiofile import async_open

from shared.utils import is_none_or_empty, replace_spaces

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
    
def __to_csv_line(data:TvProgramData, options: SaveOptions):
    data.channel = replace_spaces(data.channel)
    data.title = replace_spaces(data.title)
    if (data.description != None):
        data.description = replace_spaces(data.description)

    return (f"{escape(__format_date(data.datetime_start))}" 
    + f"{options.separator}{escape(__format_date(data.datetime_finish))}"
    + f"{options.separator}{escape(data.channel)}"
    + f"{options.separator}{escape(data.title)}"
    + f"{options.separator}{escape(data.channel_logo_url)}"
    + f"{options.separator}{escape(data.description)}"
    + f"{options.separator}{str(int(data.available_archive))}"
    + "\n")

async def __out_to_csv_async(tvPrograms: list[TvProgramData], options: SaveOptions):
    dirname = os.path.dirname(options.output_path)
    if (dirname != None and dirname != ""):
        os.makedirs(dirname, exist_ok=True)
        
    async with async_open(options.output_path, "w+") as asyncStream:
        await asyncStream.write(
            "\"datetime_start\""
            +f"{options.separator}\"datetime_finish\""
            +f"{options.separator}\"channel\""
            +f"{options.separator}\"title\""
            +f"{options.separator}\"channel_logo_url\""
            +f"{options.separator}\"description\""
            +f"{options.separator}\"available_archive\""
            +"\n")

        for tvProgram in tvPrograms:
            await asyncStream.write(
                __to_csv_line(tvProgram, options)
            )
        return

async def run_parser_out_to_csv_async(parser: TvParser, options: SaveOptions):
    parsedData = await parser.parse_async()
    await __out_to_csv_async(parsedData, options)

def run_parser_out_to_csv(parser: TvParser, options: SaveOptions):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        run_parser_out_to_csv_async(parser, options)
    )