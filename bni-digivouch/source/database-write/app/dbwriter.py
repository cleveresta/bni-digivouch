import sys, os, cx_Oracle
from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()

DBUSER = os.getenv("DBUSER")
DBPASS = os.getenv("DBPASS")
DBCONN = os.getenv("DBCONN")

if DBUSER is None or DBPASS is None or DBCONN is None:
       sys.exit("[ERROR] Exit! Database parameters are not set!")
       
TABLES = {}
TABLES["ayopop_transaction_log"] = (
    " CREATE TABLE ayopop_transaction_log (      "
     " inquiry_id           number(11) NOT NULL,  "
     " trx_date             timestamp NOT NULL,   "
     " account_num_voucher  varchar2(64) NOT NULL,"  
     " product_code         varchar2(32) NOT NULL,"  
     " transaction_id       varchar2(32) NOT NULL,"  
     " amount               number(20) NOT NULL,  "
     " account_num          varchar2(17) NOT NULL,"  
     " journal_num          varchar2(6) ,         "
     " response_code        varchar2(5) ,         "
     " response_message     varchar2(512)       "
    ") ")

TABLES["ayopop_callback_log"] = (
    "CREATE TABLE ayopop_callback_log (             "
    "      transaction_id       number(11) NOT NULL,"
    "      callback_date        timestamp NOT NULL,  "
    "      account_num_voucher  varchar(64) NOT NULL,"
    "      product_code         varchar(32) NOT NULL,"
    "      ref_number           varchar(32) NOT NULL,"
    "      amount               number(20) NOT NULL, "
    "      response_code        varchar(5) ,         "
    "      response_message     varchar(512)         "
    "    )  ")

pool = cx_Oracle.SessionPool(user=DBUSER, 
                             password=DBPASS,
                             dsn=DBCONN, 
                             min=2,
                             max=5, 
                             increment=1, 
                             encoding="UTF-8")

@app.on_event("startup")
async def startup_event():
    connection = pool.acquire()
    cursor = connection.cursor()
    table_exists = cursor.execute("SELECT table_name FROM all_tables"
                                  " WHERE table_name LIKE '%AYOPOP%'" 
                                  ).fetchall()
    if len(table_exists) == len(TABLES): pass
    else:
        for v in TABLES.values():
            cursor.execute(v)
        pool.release(connection)

@app.on_event("shutdown")
def shutdown_event():
    pool.close()

class AyopopTransaction(BaseModel):
    inquiry_id: str         
    trx_date: datetime         
    account_num_voucher: str
    product_code: str      
    transaction_id: str        
    amount: float            
    account_num: str       
    journal_num: str
    response_code: str      
    response_message: str   

class AyopopCallback(BaseModel):
    transaction_id: str     
    callback_date: datetime      
    account_num_voucher: str
    product_code: str       
    ref_number: str         
    amount: float             
    response_code: str      
    response_message: str   

class AyopopStatusUpdate(BaseModel):
    response_message: str 
    transaction_id: str             
     

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/db/transaction")
def transaction(trx: AyopopTransaction):
    connection = pool.acquire()
    cursor = connection.cursor()
    sql = """INSERT INTO ayopop_transaction_log (inquiry_id, trx_date,
                                account_num_voucher, product_code, 
                                transaction_id, amount, account_num, journal_num,
                                response_code, response_message )
             VALUES (:inquiry_id, sysdate, 
                    :account_num_voucher, :product_code, 
                    :transaction_id, :amount, :account_num, :journal_num,
                    :response_code, :response_message) """
    data = dict(inquiry_id=trx.inquiry_id, 
                account_num_voucher=trx.account_num_voucher, product_code=trx.product_code, 
                transaction_id=trx.transaction_id, amount=trx.amount, account_num=trx.account_num, journal_num=trx.journal_num,
                response_code=trx.response_code, response_message=trx.response_message
                )
    cursor.execute(sql, data)
    connection.commit()
    pool.release(connection)
    return { "status": "inserting transaction to database"}

@app.post("/db/callback")
def callback(cb: AyopopCallback):
    connection = pool.acquire()
    cursor = connection.cursor()
    sql = """INSERT INTO ayopop_callback_log (transaction_id, callback_date,
                                account_num_voucher, product_code, 
                                ref_number, amount, 
                                response_code, response_message )
             VALUES (:transaction_id, sysdate, 
                    :account_num_voucher, :product_code, 
                    :ref_number, :amount, 
                    :response_code, :response_message) """
    data = dict(transaction_id=cb.transaction_id, 
                account_num_voucher=cb.account_num_voucher, product_code=cb.product_code, 
                ref_number=cb.ref_number, amount=cb.amount,
                response_code=cb.response_code, response_message=cb.response_message
                )
    cursor.execute(sql, data)
    connection.commit()
    pool.release(connection)
    return {"status": "inserting callback to database"}

@app.post("/db/statusupdate")
def statusUpdate(upt: AyopopStatusUpdate):
    connection = pool.acquire()
    cursor = connection.cursor()
    sql = """UPDATE ayopop_transaction_log
             SET response_message = :response_message
             WHERE transaction_id = :transaction_id """
    data = dict(response_message=upt.response_message,
                transaction_id=upt.transaction_id
                )
    cursor.execute(sql, data)
    connection.commit()
    pool.release(connection)
    return { "status": "updating transaction response message"}
