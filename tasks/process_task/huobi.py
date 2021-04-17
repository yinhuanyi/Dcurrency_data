# coding: utf-8
"""
@Author: Robby
@Module name: consume_message.py
@Create date: 2020-12-21
@Function: 
"""

from multiprocessing import Event
from utils.global_logger import getlogger
from utils.const_file import  HUOBI_ERROR_LOG, HUOBI_INFO_LOG
from utils.parse_file import MySQLSessionSingleton
from model.coin import Coin
from api.huobi.spot import get_spot
from threading import Thread

huobi_logger = getlogger('huobi', HUOBI_INFO_LOG, HUOBI_ERROR_LOG)


def huobi_spot_real_time(event: Event):

    huobi_logger.info("Get Huobi Spot......")
    session = MySQLSessionSingleton._get_mysql_session()
    huobi_spots = session.query(Coin.name).filter_by(type='huobi').all()
    spot_list = []

    for item in huobi_spots:
        spot_list.append('{}usdt'.format(item[0]))

    spot_list = spot_list[:50]
    # 开启多个线程来获取数据
    for spot in spot_list:
        Thread(target=get_spot, args=(spot,), name=spot).start()


if __name__ == '__main__':
    huobi_spot_real_time(Event())