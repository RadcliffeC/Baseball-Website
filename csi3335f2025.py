import pymysql

mysql_config = {'host':'localhost',
         'user':'root',
         'password':'rootroot',
         'database':'baseball',
         'cursorclass': pymysql.cursors.Cursor
}

def get_db_connection():
    try:
        db = pymysql.connect(**mysql_config)
        cursor = db.cursor()
        return db, cursor
    except Exception as e:
        print(e)
        return None, None



