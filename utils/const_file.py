# coding: utf-8
"""
@Author: Robby
@Module name:
@Create date: 2020-11-17
@Function:
"""

import os

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(PROJECT_DIR, 'logs')
CONF_DIR = os.path.join(PROJECT_DIR, 'conf')


# PID文件
PID_FILE = os.path.join(PROJECT_DIR, 'agent.pid')


# 日志文件
AGENT_LOG = os.path.join(LOG_DIR, 'agent.log')
HUOBI_INFO_LOG = os.path.join(LOG_DIR, 'huobi_info.log')
HUOBI_ERROR_LOG = os.path.join(LOG_DIR, 'huobi_error.log')
BINANCE_INFO_LOG = os.path.join(LOG_DIR, 'binance_info.log')
BINANCE_ERROR_LOG = os.path.join(LOG_DIR, 'binance_info.log')
SQLALCHEMY_LOG = os.path.join(LOG_DIR, 'sqlalchemy_row_sql.log')

# 配置文件
SERVER_CONFIG = os.path.join(CONF_DIR, 'server.conf')


if __name__ == '__main__':
    print(PROJECT_DIR)
    print(LOG_DIR)
    print(CONF_DIR)
    print(AGENT_LOG)
    print(HUOBI_INFO_LOG)
    print(HUOBI_ERROR_LOG)
    print(BINANCE_INFO_LOG)
    print(BINANCE_ERROR_LOG)