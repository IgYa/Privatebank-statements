import requests
import hashlib
import datetime
import xml.etree.ElementTree as ET
import mytoken  # файл с паролями

# params = {'q': "python requests"}
# response = requests.get('https://api.privatbank.ua/p24api/pubinfo?exchange&json&coursid=11')  # курс- безнал
# response = requests.get('https://api.privatbank.ua/p24api/pubinfo?json&exchange&coursid=5')  # курс- нал
#response = requests.post('https://api.privatbank.ua/p24api/rest_fiz')  # выписки

# for key in response.headers:
#     print(f'{key} : {response.headers[key]}')
# print()
#
# print(response.text)
# for i in response.json():
#     for key in i:
#         print(f'{key} : {i[key]}')
#     print()

def date_sd():
    time_now = datetime.datetime.now() - datetime.timedelta(days=period)
    str_time = time_now.strftime("%d.%m.%Y")
#    str_time = '01.08.2022'
    return str_time

def date_ed():
    time_now = datetime.datetime.now()
    str_time = time_now.strftime("%d.%m.%Y")
    return str_time


# даты начала и конца периода
period = int(input("Введите период запрашиваемой выписки (от сегодня): "))
sd = date_sd()
ed = date_ed()

# формулюємо тіло запиту
url = "https://api.privatbank.ua/p24api/rest_fiz"  # змінна в яку записано посилання до сайту

# складається тіло запиту
head = f"""<?xml version="1.0" encoding="UTF-8"?>
        <request version="1.0">
        <merchant>
        <id>{mytoken.ID}</id>   
        <signature>"""
data = f"""<oper>cmt</oper>
                    <wait>0</wait>
                    <test>0</test>
                    <payment id="">
                        <prop name="sd" value="{sd}" />
                        <prop name="ed" value="{ed}" />
                        <prop name="card" value="{mytoken.CARD}" />
                    </payment>"""
end_head = """</signature>
            </merchant>
            <data>
                """
footer = """
    </data>
    </request>"""

# шифруємо пароль
signature_md5 = hashlib.md5((data + mytoken.PASSWORD).encode('utf-8')).hexdigest()
signature_done = hashlib.sha1(signature_md5.encode('utf-8')).hexdigest()

# складаємо тіло запиту
data_done = head + signature_done + end_head + data + footer
# print(data_done)
# print()


# робимо post запит
res = requests.post(url, data=data_done, headers={'Content-Type': 'application/xml; charset=UTF-8'})
print(res.status_code)
if res:
    print('STATUS - OK!')
print()
print(sd, ed, sep=' - ')
# print(res.text)
# print()

# Задание 6
# Настройте интеграцию с API своего банка для автоматической загрузки операций по карте

import sqlite3
from sqlite3 import Error


def create_connection(path):
    connection = None
    try:
        connection = sqlite3.connect(path)
        print(f"Connection to SQLite DB {path} successfully")
    except Error as e:
        print(f"The error '{e}' occurred")

    return connection


def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query executed successfully")
    except Error as e:
        print(f"The error '{e}' occurred")


def execute_read_query(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as e:
        print(f"The error '{e}' occurred")



connection = create_connection('06.sqlite')  # "./data/sqliteDB" или :memory:

create_table_bank_statement = """
CREATE TABLE IF NOT EXISTS bank_statement (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    card TEXT,
    appcode TEXT,
    trandate TEXT NOT NULL,
    trantime TEXT NOT NULL,
    amount TEXT NOT NULL,
    cardamount TEXT NOT NULL,
    rest TEXT NOT NULL,
    terminal TEXT,
    description TEXT NOT NULL
);
"""
execute_query(connection, create_table_bank_statement)
print()

# робимо разбор xml файла
root = ET.fromstring(res.text)
statements = root.find('data/info/statements')
#print(statements.attrib)    # .attrib- доступ к атрибутам тега

for statement in statements:
    print(statement.attrib)
    v = tuple(statement.attrib.values())
    print(v)

    # вставляем данные в таблицу
    insert_bank_statement = f""" 
        INSERT INTO bank_statement (card, appcode, trandate, trantime, amount, cardamount, rest, terminal, description) VALUES {v};     
        """
    execute_query(connection, insert_bank_statement)
    print()

#  Печатаем данные из таблицы bank_statement
select_bank_statement = "SELECT * from bank_statement"
bank_statement = execute_read_query(connection, select_bank_statement)

for statement in bank_statement:
    print(statement)
