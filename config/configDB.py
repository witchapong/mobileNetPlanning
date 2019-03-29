import pymysql


class Database:
    def __init__(self):
        host = "127.0.0.1"
        user = "root"
        password = "root"
        db = "mp_bkk"
        port = 8889
        self.con = pymysql.connect(host=host,
                                   user=user,
                                   password=password,
                                   db=db,
                                   port=port,
                                   cursorclass=pymysql.cursors.
                                   DictCursor)

        self.cur = self.con.cursor()
