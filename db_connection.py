import pymysql
from csi3335f2025 import mysql

def get_db_connection():
    try:
        db = pymysql.connect(**mysql)
        cursor = db.cursor()
        return db, cursor
    except Exception as e:
        print(e)
        return None, None