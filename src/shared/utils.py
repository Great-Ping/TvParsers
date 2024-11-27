from datetime import datetime, timedelta
from typing import Union
from .models import TvProgramData

def get_monday_datetime(timezone):
    now = datetime.now(timezone)
    now -= timedelta(days=now.weekday())
    return now

def format_date(date: Union[datetime, None]):
    if (date is None):
        return ""

    return date.isoformat("T", "seconds")

#Заполняет дату и время для каждой программы, 
#основываясь на дате начала предыдущей программы.
#Для последней программы дата окончания 23:59 этого же дня
def fill_finish_date_by_next_start_date(tv_programs: list[TvProgramData]):
    for i in range(1, len(tv_programs)):
        tv_programs[i-1].datetime_finish = tv_programs[i].datetime_start

    if (len(tv_programs) == 0):
        return 
    last_program = tv_programs[-1]
    last_program.datetime_finish = last_program.datetime_start.replace(
        hour=23,
        minute=59
    )


def is_none_or_empty(string: str):
    if (string is None):
        return True
    
    return string != "" or string != " " or string != "\t" or string != "\n"