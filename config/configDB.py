import pymysql


class Development:
    host = "127.0.0.1"
    user = "root"
    password = "root"
    db = "mp_bkk"
    port = 8889


class Production:
    host = "10.198.48.136"
    user = "admin"
    password = "rpoadmin"
    db = "mp_bkk"
    port = 3306


class Database:
    def __init__(self):
        config = Development()  # set configuration environment
        self.con = pymysql.connect(host=config.host,
                                   user=config.user,
                                   password=config.password,
                                   db=config.db,
                                   port=config.port,
                                   cursorclass=pymysql.cursors.
                                   DictCursor)  # connection object

        self.cur = self.con.cursor()  # cursor object
