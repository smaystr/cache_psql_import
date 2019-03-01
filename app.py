from database import Database, ConnectionCursor
import json

# import warnings
# import re
# from sqlalchemy import create_engine

# warnings.simplefilter('ignore')

Database.set_connection(host='192.168.31.103', database='cache', user='postgres', password='')
# Database.set_connection(host='localhost', database='cache', user='postgres', password='asd123')


def fix_json(filename):

    with open(filename, encoding='cp1251') as f:
        with open(filename + '.out', "w") as f1:
            for line in f:
                if line.startswith('{') or line.startswith('}') or line.endswith(': {\n'):
                    f1.write(line)
                else:
                    if line.startswith('"') and len(line) > 3:
                        newline = line
                    else:
                        newline = newline.replace('\n', '') + line
                    print(line.endswith('",\n'), line.endswith('"\n'), not line.endswith('\"\n'))
                    print(newline, line)
                    if line.endswith('",\n') or (line.endswith('"\n') and not line.endswith('\"\n')):
                        f1.write(newline)


def from_json(filename):

    with ConnectionCursor() as cursor:
        cursor.execute('DROP TABLE IF EXISTS public.data')
        cursor.execute('CREATE TABLE public.data ( '
                       'id serial PRIMARY KEY, '
                       'article_id integer, '
                       'title_id character varying(20), '
                       'number integer, '
                       'field_value text, '
                       'CONSTRAINT fk_title_data FOREIGN KEY(title_id) '
                       'REFERENCES public.titles(id) MATCH SIMPLE '
                       'ON UPDATE NO ACTION '
                       'ON DELETE NO ACTION);')

    with open(filename) as f:
        json_data = json.load(f)

        with ConnectionCursor() as cursor:
            i = 0
            for item in json_data.values():
                i += 1
                for key in item:
                    article_id = key[:key.index(',')]
                    title_id = key[key.index(',')+1:]
                    number = '0'

                    if title_id.startswith('lit'):
                        number = title_id[title_id.rindex(',')+1:]
                        title_id = title_id[:title_id.rindex(',')]

                    if not (title_id.startswith('8') or title_id.startswith('9')):
                        cursor.execute('INSERT INTO public.data (article_id, title_id, number, field_value) '
                                       'VALUES (%s, %s, %s, %s)', (article_id, title_id, number, item[key]))

                if i % 100 == 0:
                    print("Обработано {} записей".format(i))


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

# file = "data/datan2.txt"
file = "data/test"
fix_json(file)

# file = "data/datan2.txt.out"
# from_json(file)
