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
    
    return string == "" or string == " " or string == "\t" or string == "\n" or string == "\r"


#рекурсивный обход узла, возвращающий текст без тэгов
#игнорирует тэг br
def get_node_text(node):
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

def replace_spaces(string: str):
    start = 0
    end = len(string)
    for i in string:
        if (not is_none_or_empty(i)):
            break
        start += 1

    for i in reversed(string):
        if (not is_none_or_empty(i)):
            break
        end -= 1
    
    return string[start: end]