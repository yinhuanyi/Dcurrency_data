# coding: utf-8
"""
@Author: Robby
@Module name: spot.py
@Create date: 2021-04-13
@Function: 
"""

import json
import sys
import traceback
import socket
from datetime import datetime
from time import sleep
from threading import Lock, Thread
import websocket
import zlib
from utils.global_logger import getlogger
from utils.const_file import  HUOBI_ERROR_LOG, HUOBI_INFO_LOG

huobi_logger = getlogger('huobi', HUOBI_INFO_LOG, HUOBI_ERROR_LOG)

class HuoWetsocket:
    # 初始化
    def __init__(self, host=None, ping_interval=20):


        self.host = host
        self.ping_interval = ping_interval
        # 线程锁
        self._ws_lock = Lock()
        # ws客户端对象
        self._ws = None
        # 工作线程
        self._worker_thread = None
        # ping线程
        self._ping_thread = None
        # 是否启动websocket开关
        self._active = False

        # debug需要，
        # 最后发送的消息
        self._last_sent_text = None
        # 最后接收的消息
        self._last_received_text = None


    def start(self, spot):

        # 打开消息开关
        self._active = True

        # 开启工作线程
        self._worker_thread = Thread(target=self._run, args=(spot, ))
        self._worker_thread.start()

        # 开启ping线程
        self._ping_thread = Thread(target=self._run_ping, )
        self._ping_thread.start()

    def stop(self):
        """
        停止客户端.
        """
        self._active = False
        self._disconnect()

    def join(self):
        """
        Wait till all threads finish.
        This function cannot be called from worker thread or callback function.
        """
        self._ping_thread.join()
        self._worker_thread.join()

    def send_msg(self, msg: dict):
        """
        向服务器发送数据.
        如果你想发送非json数据，可以重写该方法.
        """
        text = json.dumps(msg)
        self._record_last_sent_text(text)
        return self._send_text(text)

    def _send_text(self, text: str):
        """
        发送文本数据到服务器.
        """
        ws = self._ws
        if ws:
            ws.send(text, opcode=websocket.ABNF.OPCODE_TEXT)

    def _ensure_connection(self, spot):

        triggered = False
        # 申请一把线程锁
        with self._ws_lock:
            if self._ws is None:
                # 创建一个ws连接对象
                self._ws = websocket.create_connection(self.host)
                # 设置trigger为true
                triggered = True
        if triggered:
            self.on_open(spot)

    # 当没有收到websocket数据，断开连接
    def _disconnect(self):

        triggered = False
        with self._ws_lock:
            if self._ws:

                ws: websocket.WebSocket = self._ws
                self._ws = None

                triggered = True

        if triggered:
            # 关闭websocket连接
            ws.close()
            self.on_close()

    def _run(self, spot):

        try:
            while self._active:
                try:
                    # 开启一个连接
                    self._ensure_connection(spot)
                    ws = self._ws
                    if ws:
                        # 在_ensure_connection中订阅了频道，获取数据
                        text = ws.recv()

                        # 如果没有接收到数据
                        if not text:
                            # 断开连接，并且再次创建一个websocket连接，订阅频道获取数据
                            self._disconnect()
                            continue
                        # 每次保存最后1000条数据
                        self._record_last_received_text(text)
                        # 将text的压缩数据传递到on_msg方法进行解压
                        self.on_msg(text)
                # ws is closed before recv function is called
                # For socket.error, see Issue #1608
                except (websocket.WebSocketConnectionClosedException, socket.error):
                    self._disconnect()

                # other internal exception raised in on_msg
                except:  # noqa
                    et, ev, tb = sys.exc_info()
                    self.on_error(et, ev, tb)
                    self._disconnect()  #

        except:  # noqa
            et, ev, tb = sys.exc_info()
            self.on_error(et, ev, tb)

        self._disconnect()

    def _run_ping(self):
        """"""
        while self._active:
            try:
                self._ping()
            except:  # noqa
                et, ev, tb = sys.exc_info()
                self.on_error(et, ev, tb)
                sleep(1)

            for i in range(self.ping_interval):
                if not self._active:
                    break
                sleep(1)

    def _ping(self):
        """"""
        ws = self._ws
        if ws:
            ws.send("ping", websocket.ABNF.OPCODE_PING)

    # 连接打开，并且订阅流
    def on_open(self, spot):
        print("on open")

        # data = {"op": "subscribe", "args": ["swap/depth5:BTC-USD-SWAP"]}
        data = {"sub":"market.{}.trade.detail".format(spot), "id": 1}
        self.send_msg(data)

    def on_close(self):
        """
        on close websocket
        """

    def on_msg(self, data: str):
        # print(data)
        msg = json.loads(zlib.decompress(data, 31))
        if msg.get('tick'):
            spot_name = msg.get('ch').split('.')[1]
            tick = msg.get('tick')
            data = tick.get('data')
            spot_price = data[0].get('price')

            huobi_logger.info('{}={}'.format(spot_name, spot_price))

            import redis
            from utils.parse_file import RedisPoolSingleton

            pool = RedisPoolSingleton._get_redis_pool()
            with redis.Redis(connection_pool=pool) as r:
                r.set(spot_name, spot_price)


    def on_error(self, exception_type: type, exception_value: Exception, tb):
        """
        Callback when exception raised.
        """
        sys.stderr.write(
            self.exception_detail(exception_type, exception_value, tb)
        )

        return sys.excepthook(exception_type, exception_value, tb)

    def exception_detail(
            self, exception_type: type, exception_value: Exception, tb
    ):
        """
        Print detailed exception information.
        """
        text = "[{}]: Unhandled WebSocket Error:{}\n".format(
            datetime.now().isoformat(), exception_type
        )
        text += "LastSentText:\n{}\n".format(self._last_sent_text)
        text += "LastReceivedText:\n{}\n".format(self._last_received_text)
        text += "Exception trace: \n"
        text += "".join(
            traceback.format_exception(exception_type, exception_value, tb)
        )
        return text

    def _record_last_sent_text(self, text: str):
        """
        Record last sent text for debug purpose.
        """
        self._last_sent_text = text[:1000]

    def _record_last_received_text(self, text: str):

        self._last_received_text = text[:1000]


def get_spot(spot):
    okex_ws = HuoWetsocket(host="wss://api.huobi.pro/ws", ping_interval=20)
    okex_ws.start(spot)

if __name__ == '__main__':
    # 这个数据从数据库里面读取
    spot_list = ['btcusdt', 'ethusdt', 'fil3lusdt']
    # 开启多个线程来获取数据
    for spot in spot_list:
        Thread(target=get_spot, args=(spot,), name=spot).start()
