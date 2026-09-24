import mysql.connector
from config import *

def connect():
    return mysql.connector.connect(host=DB_HOST,port=DB_PORT,user=DB_USER,password=DB_PASSWORD,database=DB_NAME)

def query(sql, params=()):
    c=connect(); cur=c.cursor(dictionary=True)
    try:
        cur.execute(sql,params); return cur.fetchall()
    finally: cur.close(); c.close()

def run(sql, params=()):
    c=connect(); cur=c.cursor()
    try:
        cur.execute(sql,params); c.commit(); return cur.lastrowid
    except: c.rollback(); raise
    finally: cur.close(); c.close()
