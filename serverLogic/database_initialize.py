import sqlite3 as sql 

DATABASE_PATH = "./server.db"

db_conn = sql.connect(DATABASE_PATH)
print("Sucessfully Connect!")

db_cursor = db_conn.cursor()

# sql_command = '''
# CREATE TABLE user(
# id TEXT PRIMARY KEY ,
# nickname TEXT NOT NULL,
# password TEXT NOT NULL,
# status TEXT NOT NULL
# );
# '''

# sql_command = '''
# CREATE TABLE group(
# id INTEGER PRIMARY KEY AUTOINCREMENT,
# user1 TEXT NOT NULL,
# user2 TEXT NOT NULL
# );
# '''


# sql_command = '''

# CREATE TABLE usergroup(
# id TEXT PRIMARY KEY ,
# name TEXT NOT NULL,
# master TEXT NOT NULL
# );
# '''

# sql_command = '''
# CREATE TABLE grouprelation(
# id INTEGER PRIMARY KEY AUTOINCREMENT,
# groupid TEXT ,
# userid TEXT
# );
# '''

# sql_command = '''
# CREATE TABLE message(
# id INTEGER PRIMARY KEY AUTOINCREMENT,
# initial TEXT NOT NULL,
# terminal TEXT NOT NULL,
# via TEXT NOT NULL,
# type TEXT NOT NULL,
# unreadflag TEXT NOT NULL,
# datetime TEXT NOT NULL,
# content TEXT NOT NULL
# );
# '''


# sql_command = '''
# INSERT INTO user(id,nickname,password,status)
# VALUES("A11","test","123","offline")
# '''

# sql_command = '''
# CREATE TABLE file(
# id INTEGER PRIMARY KEY AUTOINCREMENT,
# originalname TEXT NOT NULL,
# storagename TEXT NOT NULL,
# initial TEXT NOT NULL ,
# via TEXT NOT NULL,
# terminal TEXT NOT NULL,
# type TEXT NOT NULL,
# status TEXT NOT NULL,
# datetime NOT NULL
# )
# '''

sql_command = '''
CREATE TABLE groupmanager(
id INTEGER PRIMARY KEY AUTOINCREMENT ,
groupid TEXT NOT NULL ,
userid TEXT NOT NULL 
)
'''


db_cursor.execute(sql_command)
db_conn.commit() 
print("Successfully Commit!")
print
db_conn.close() 