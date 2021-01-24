import pymysql
from loguru import logger


class MySQL:
    _ip = "your database host"
    _user = "test"
    _passwd = "test"
    _port = 3306
    _database = "proxy"

    arguments_keys = {'ip', 'port', 'user', 'password', 'database'}

    @classmethod
    def conn_mysql(cls, ip=None, user=None, passwd=None, port=None, database=None):
        if ip is None and user is None and passwd is None and port is None and database is None:
            db = pymysql.connect(host=MySQL._ip, user=MySQL._user, passwd=MySQL._passwd, port=MySQL._port
                                 , database=MySQL._database, charset='utf8')
        else:
            db = pymysql.connect(host=ip, user=user, passwd=passwd, port=int(port), database=database, charset='utf8')
        return db

    @classmethod
    def connect(cls, arguments=None, ip=None, user=None, passwd=None, port=None, database=None):
        if arguments:
            assert isinstance(arguments, dict) and set(arguments.keys()) == cls.arguments_keys
            return pymysql.connect(
                host=arguments.get('ip'), port=int(arguments.get('port')), user=arguments.get('user'),
                passwd=arguments.get('password'), database=arguments.get('database'), charset='utf8'
            )
        return pymysql.connect(
            host=ip or cls._ip, port=port or cls._port, user=user or cls._user,
            passwd=passwd or cls._passwd, database=database or cls._database
        )

    @classmethod
    def run_sql(cls, sql, db=None):
        try:
            db = MySQL.conn_mysql() if db is None else db
            cursor = db.cursor()
            cursor.execute(sql)
            db.commit()
        except pymysql.MySQLError as e:
            logger.error(e)
            db.rollback()
            # 如果插入不关闭就注释掉下面的close（）
        # finally:
        #     db.close()

    @classmethod
    def execute_sql(cls, sql, db=None):
        try:
            db = MySQL.conn_mysql() if db is None else db
            cursor = db.cursor()
            cursor.execute(sql)
            db.commit()
        except pymysql.MySQLError as e:
            logger.error(e)
            db.rollback()

    @classmethod
    def sel_table(cls, sql, db=None):
        try:
            db = MySQL.conn_mysql() if db is None else db
            cursor = db.cursor()
            cursor.execute(sql)
            while 1:
                row = cursor.fetchone()
                if row is not None:
                    yield row
                else:
                    break
        finally:
            pass
            # db.close()

    @classmethod
    def sel_table1(cls, sql, db=None):
        db = MySQL.conn_mysql() if db is None else db
        cursor = db.cursor()
        cursor.execute(sql)
        while 1:
            row = cursor.fetchone()
            if row is not None:
                yield row
            else:
                break

    @classmethod
    def sel_table2(cls, sql, db=None):
        db = MySQL.conn_mysql() if db is None else db
        cursor = db.cursor()
        cursor.execute(sql)
        while 1:
            row = cursor.fetchone()
            if row is not None:
                yield row
            else:
                break

    @classmethod
    def sel_table3(cls, sql, db=None):
        db = MySQL.conn_mysql() if db is None else db
        cursor = db.cursor()
        cursor.execute(sql)
        row = cursor.fetchall()[0][0]
        # db.close()
        return row

    @classmethod
    def sel_table6(cls, sql, db=None):
        db = MySQL.conn_mysql() if db is None else db
        cursor = db.cursor()
        cursor.execute(sql)
        row = cursor.fetchall()[0][0]
        return row