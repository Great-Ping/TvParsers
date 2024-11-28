from datetime import datetime
from typing import Union
from .options import ParserOptions

class TvProgramData:
    #формате YYYY-mm-ddThh:mm:ss+tz:tz (пример - 2024-07-22T16:27:01+00:00)
    datetime_start: datetime
    #формате YYYY-mm-ddThh:mm:ss+tz:tz (пример - 2024-07-22T16:27:01+00:00)
    datetime_finish: Union[datetime, None]
    #channel - строка - название телеканала
    channel: str
    #строка - название телепередачи
    title: str
    #строка - URL на изображение телеканала
    channel_logo_url: Union[str, None]
    #строка - описание телепередачи
    description: Union[str, None]
    #число 1 или 0 - доступность архива
    available_archive: bool

    def __init__(
        self, 
        datetime_start: datetime, 
        datetime_finish: Union[datetime, None],
        channel: str,
        title: str,
        channel_logo_url: Union[str, None],
        description: Union[str, None],
        available_archive: bool
    ):
        self.datetime_start = datetime_start
        self.datetime_finish = datetime_finish
        self.channel = channel
        self.title = title

        self.channel_logo_url = channel_logo_url
        self.description = description
        self.available_archive = available_archive

class TvParser:    
    options: ParserOptions

    def __init__(self, options: ParserOptions) -> None:
        self.options = options


    def in_config_time_interval(self, time):
        if (self.options.start_date != None and time < self.options.start_date):
            return False
        
        if (self.options.finish_date != None and time > self.options.finish_date):
            return False
        
        return True

    async def parse_async(self) ->  list[TvProgramData]:
        pass


