from database import Database, ConnectionCursor
import json

# import warnings
# import re
# from sqlalchemy import create_engine

# warnings.simplefilter('ignore')

Database.set_connection(host='192.168.31.103', database='cache', user='postgres', password='')
# Database.set_connection(host='localhost', database='cache', user='postgres', password='asd123')


def from_json(filename):

    with ConnectionCursor() as cursor:
        cursor.execute('DROP TABLE IF EXISTS public.data')
        cursor.execute('CREATE TABLE public.data ( '
                       'id serial PRIMARY KEY, '
                       'article_id integer, '
                       'title_id character varying(20), '
                       'field_value text, '
                       'CONSTRAINT fk_title_data FOREIGN KEY(title_id) '
                       'REFERENCES public.titles(id) MATCH SIMPLE '
                       'ON UPDATE NO ACTION '
                       'ON DELETE NO ACTION);')

    with open(filename, encoding='cp1251') as f:
        json_data = json.load(f)

        with ConnectionCursor() as cursor:
            for item in json_data.values():
                for key in item:
                    article_id = key[:key.index(',')]
                    title_id = key[key.index(',')+1:]

                    if not (title_id.startswith('8') or title_id.startswith('9')):
                        cursor.execute('INSERT INTO public.data (article_id, title_id, field_value) '
                                       'VALUES (%s, %s, %s)', (article_id, title_id, item[key]))

                    # print(article_id, "|", title_id, "|", key, "|", item[key])


def from_file(filename):
    data = []
    with open(filename, encoding='utf-8') as f:
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
        cursor.execute('DROP TABLE IF EXISTS public.titles')
        cursor.execute('CREATE TABLE public.titles ( '
                       'id character varying(20) PRIMARY KEY, '
                       'name character varying(200) NOT NULL )')
        for item in data_set:
            cursor.execute('INSERT INTO public.titles (id, name) VALUES (%s, %s)', (item['key'], item['name']))


# create_title_table()

file = "data/DATAnn"
from_json(file)
