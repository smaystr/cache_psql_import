from database import Database, ConnectionCursor
import json

# import warnings
# import re
# from sqlalchemy import create_engine

# warnings.simplefilter('ignore')

Database.set_connection(host='192.168.31.103', database='cache', user='postgres', password='')


def from_json(filename):
    with open(filename, encoding='utf-8') as f:
        json_data = json.load(f)

        for item in json_data.values():
            for key in item:
                print(key, item[key])


# file = "data/cachedb_dump.json"
# from_json(file)


def from_file(filename):
    data = []
    with open(filename, "r") as f:
        content = f.read().splitlines()
        for line in content:
            row_data = line.split(":")
            row = {'key': row_data[0],
                   'name': row_data[1]
                   }
            data.append(row)

    return data


def create_title_table():
    filename = "data/titles.txt"
    data_set = from_file(filename)

    with ConnectionCursor() as cursor:
        cursor.execute('CREATE OR REPLACE TABLE public.titles ( '
                       'id character varying(20) PRIMARY KEY, '
                       'name character varying(200) NOT NULL )')
        for item in data_set:
            cursor.execute('INSERT INTO public.titles (id, name) VALUES (%s, %s)', (item['key'], item['name']))


# create_title_table()
