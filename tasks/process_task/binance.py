# coding: utf-8
"""
@Author: Robby
@Module name:
@Create date: 2020-11-17
@Function: 
"""

from multiprocessing import Event
from utils.global_logger import getlogger
from utils.const_file import  BINANCE_INFO_LOG, BINANCE_ERROR_LOG
from utils.parse_file import MySQLSessionSingleton
from model.coin import Coin
from api.binance.spot import get_spot
from threading import Thread

binance_logger = getlogger('binance', BINANCE_INFO_LOG, BINANCE_ERROR_LOG)


def binance_spot_real_time(event: Event):

    binance_logger.info("Get Binance Spot......")
    session = MySQLSessionSingleton._get_mysql_session()
    huobi_spots = session.query(Coin.name).filter_by(type='binance').all()
    spot_list = []

    for item in huobi_spots:
        spot_list.append('{}usdt'.format(item[0]))

    Thread(target=get_spot, args=(spot_list,), name='spot_list').start()


if __name__ == '__main__':
    binance_spot_real_time(Event())