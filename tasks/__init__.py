# coding: utf-8
"""
@Author: Robby
@Module name: __init__.py.py
@Create date: 2020-12-21
@Function: 
"""

from multiprocessing import Process
from utils.global_logger import getlogger
from utils.parse_file import EventSingleton
from utils.const_file import AGENT_LOG
from .process_task.binance import binance_spot_real_time
from .process_task.huobi import huobi_spot_real_time


engine_logger = getlogger(logger_name='engine', info_file_path=AGENT_LOG, error_file_path=AGENT_LOG)

def start_engine():
    global_event = EventSingleton.getEventInstance()
    Process(target=huobi_spot_real_time, args=(global_event,), name='huobi_spot').start()
    Process(target=binance_spot_real_time, args=(global_event,), name='binance_spot').start()
    engine_logger.info("Spot Start......")


if __name__ == '__main__':
    start_engine()