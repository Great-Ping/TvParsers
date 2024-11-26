from datetime import datetime
from typing import Union

class CompilerOptions:
    #с какого числа
    start_date: Union[datetime, None]
    #по какое число включительно 
    #но не факт что будут передачи за этот период
    finish_date: datetime

    def __init__(
        self,
        start_date,
        finish_date
    ):
        self.start_date = start_date
        self.finish_date = finish_date

class SaveOptions:
    output_path: str

    def __init__(
        self,
        output_path: str
    ):
        self.output_path = output_path


class Options:
    compiler_config: CompilerOptions
    save_config: SaveOptions
    
    def __init__(
        self,
        compiler_config: CompilerOptions,
        save_config: SaveOptions
    ):
        self.compiler_config = compiler_config
        self.save_config = save_config

    
