from datetime import datetime, UTC
from typing import Union
from argparse import ArgumentParser

class ParserOptions:
    #с какого числа
    start_date: Union[datetime, None]
    #по какое число включительно 
    #но не факт что будут передачи за этот период
    finish_date: Union[datetime, None]

    def __init__(
        self,
        start_date: Union[datetime, None] = None,
        finish_date: Union[datetime, None] = None
    ):
        self.start_date = start_date
        self.finish_date = finish_date

class SaveOptions:
    output_path: str
    separator: str
    def __init__(
        self,
        output_path: str,
        separator: str = "\t"
    ):
        self.separator = separator
        self.output_path = output_path


class Options:
    parser_options: ParserOptions
    save_options: SaveOptions
    
    def __init__(
        self,
        parser_options: ParserOptions,
        save_options: SaveOptions
    ):
        self.parser_options = parser_options
        self.save_options = save_options


def create_default_arg_parser() -> ArgumentParser:
    args_parser = ArgumentParser()
    args_parser.add_argument("-sd", "--start-date")
    args_parser.add_argument("-fd", "--finish-date")
    args_parser.add_argument("-o", "--output")
    args_parser.add_argument("-sep", "--separator")

    return args_parser

def read_command_line_options() -> Options:
    parser = create_default_arg_parser()
    args = parser.parse_args()
    
    start_date = None
    finish_date = None
    save_output = "./out.csv"
    separator = '\t'

    if (args.start_date is not None):
        start_date = datetime.strptime(args.start_date, "%Y-%m-%d").replace(tzinfo=UTC)
    if (args.start_date is not None):
        finish_date = datetime.strptime(args.finish_date, "%Y-%m-%d").replace(tzinfo=UTC)

    if (args.output is not None):
        save_output = args.output

    if (args.separator is not None):
        separator = args.separator

    print(separator)

    parser_options = ParserOptions(start_date, finish_date)
    save_options = SaveOptions(save_output, separator)

    return Options(parser_options, save_options)