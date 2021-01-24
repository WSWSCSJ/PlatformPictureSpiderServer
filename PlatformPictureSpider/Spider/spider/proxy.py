"""
@Author: CXJ
"""
import random
from Spider.spider.mysql import MySQL

IP = 'your database host'
USER = 'test'
PASSWORD = 'test'
PORT = 3306
DATABASE = 'proxy'
TABLE = 'proxies'

class Proxy:
    """
    私有化,后续与mysql合并避免变量名冲突
    """
    __connection = None

    def __init__(self, ip=IP, user=USER, passwd=PASSWORD, port=PORT, database=DATABASE, table=TABLE):
        self.ip = ip
        self.user = user
        self.passwd = passwd
        self.port = port
        self.database = database
        self.table = table
        self.init_connection()

    def init_connection(self):
        if not self.__connection:
            self.__connection = MySQL.conn_mysql(
                self.ip, self.user, self.passwd, self.port, self.database
            )

    @property
    def connection(self):
        """
        每次获取ip前进行数据库连接是否断开检测
        """
        if not self.__connection:
            self.init_connection()
        return self.__connection

    @property
    def proxies(self):
        _proxies = {}
        con = self.connection
        con.ping(reconnect=True)
        cur = con.cursor()
        rows = cur.execute("select http, https from {table} limit {number},1".format(table=self.table, number=int(random.randint(1, 20))))
        if rows == 1:
            row = cur.fetchone()
            _proxies['http'] = row[0]
            _proxies['https'] = row[1]
        return _proxies

GlobalProxy = Proxy()