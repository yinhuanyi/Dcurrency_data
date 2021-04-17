# coding: utf-8
"""
@Author: Robby
@Module name: parse_file.py
@Create date: 2020-10-28
@Function: 全局单例
"""

from configparser import ConfigParser
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from utils.const_file import SERVER_CONFIG, SQLALCHEMY_LOG
from utils.encrypt_decrypt import decrypt
from utils.global_logger import getlogger
from multiprocessing import Event
import redis

# 基础配置
class SingletonBase:
    __parser = None

    @classmethod
    def _get_parser(cls):
        if cls.__parser == None:
            cls.__parser = ConfigParser()
            cls.__parser.read(SERVER_CONFIG)
        return cls.__parser

# MySQL配置
class MySQLConfigSingleton(SingletonBase):
    __mysql_config_info = None

    @classmethod
    def _get_mysql_config_info(cls):
        if cls.__mysql_config_info == None:
            parser = cls._get_parser()
            mysql_ip = parser.get('MySQL', 'IP')
            mysql_port = parser.get('MySQL', 'PORT')
            mysql_database = parser.get('MySQL', 'DATABASE')
            mysql_user = parser.get('MySQL', 'USER')
            mysql_password = parser.get('MySQL', 'PASSWORD')

            cls.__mysql_config_info = mysql_ip, mysql_port, mysql_database, mysql_user, decrypt(mysql_password)

        return cls.__mysql_config_info

# 数据库engine单例
class MySQLEngineSingleton:
    __engine = None

    @classmethod
    def _get_mysql_engine(cls):
        if cls.__engine == None:
            mysql_ip, mysql_port, mysql_database, mysql_user, mysql_password = MySQLConfigSingleton._get_mysql_config_info()
            engine = create_engine('mysql+pymysql://{user}:{password}@{mysql_ip}:{port}/{database}?charset=utf8mb4'
                                   .format(user=mysql_user, password=mysql_password, mysql_ip=mysql_ip, port=mysql_port, database=mysql_database),
                                    echo=False,
                                    pool_size=30,
                                    pool_recycle=3600,
                                    encoding='utf-8',
                                    max_overflow=3000)

            # 配置日志，SQLalchemy的CRUD操作日志，都会显示在这里
            getlogger('sqlalchemy.engine', SQLALCHEMY_LOG, SQLALCHEMY_LOG)
            cls.__engine = engine
        return cls.__engine

# 获取MySQLbase
class SQLAlchemyBaseSingleton:
    __Base = None

    @classmethod
    def _get_sqlalchemy_base(cls):
        if cls.__Base == None:
            cls.__Base = declarative_base()
        return cls.__Base

# 数据库session会话
class MySQLSessionSingleton:
    __Session = None

    @classmethod
    def _get_mysql_session(cls):
        # 初始化的时候扫描数据表
        if cls.__Session == None:
            from model import coin
        Base = SQLAlchemyBaseSingleton._get_sqlalchemy_base()
        engine = MySQLEngineSingleton._get_mysql_engine()
        Base.metadata.create_all(engine)
        session = sessionmaker(bind=engine)
        cls.__Session = session
        return session()

# Redis配置
class RedisConfigSingleton(SingletonBase):
    __redis_config_info = None

    @classmethod
    def _get_redis_config_info(cls):
        if cls.__redis_config_info == None:
            parser = cls._get_parser()
            redis_ip = parser.get('Redis', 'IP')
            redis_port = parser.get('Redis', 'PORT')
            cls.__redis_config_info = redis_ip, int(redis_port)


        return cls.__redis_config_info

# Redis连接池单例
class RedisPoolSingleton:
    __redis_pool = None

    @classmethod
    def _get_redis_pool(cls):
        if cls.__redis_pool == None:
            try:
                redis_ip, redis_port = RedisConfigSingleton._get_redis_config_info()
            except Exception as e:
                pass
                # TODO: 如果出现异常, 先写死
                redis_ip, redis_port = '127.0.0.1', 6379
            cls.__redis_pool = redis.ConnectionPool(host=redis_ip, port=redis_port, decode_responses=True, db=0)
        return cls.__redis_pool

# 事件单例
class EventSingleton:
    __event = None

    @classmethod
    def getEventInstance(cls):
        if  cls.__event == None:
            cls.__event = Event()
        return cls.__event

if __name__ == '__main__':
    pass