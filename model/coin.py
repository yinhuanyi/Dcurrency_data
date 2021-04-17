# coding: utf-8
"""
@Author: Robby
@Module name: coin.py
@Create date: 2021-04-08
@Function: 
"""


from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Index
from utils.parse_file import SQLAlchemyBaseSingleton
Base = SQLAlchemyBaseSingleton._get_sqlalchemy_base()

"""
class Coin(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, verbose_name="名称")
    type = models.CharField(max_length=100, verbose_name="属于哪个所", blank=True, null=True)

    class Meta:
        verbose_name = "名称"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name
"""

class Coin(Base):
    __tablename__ = 'trades_coin'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, doc='名称', comment='名称')
    type = Column(String(100), nullable=False, doc='属于哪个所', comment='属于哪个所')
    create_time = Column(DateTime, nullable=False, doc='名称', comment='名称')
    modify_time = Column(DateTime, nullable=False, doc='名称', comment='名称')

    __table_args__ = {'mysql_engine': 'InnoDB',
                      'mysql_collate': 'utf8mb4_general_ci',
                      'mysql_charset': 'utf8mb4',}