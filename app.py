# import warnings
import psycopg2
import json


# import re
# from sqlalchemy import create_engine

# warnings.simplefilter('ignore')


def from_json(filename):
    with open(filename) as f:
        json_data = json.load(f)

    for entity in json_data:
        print(entity)


def conn_psql(command):
    conn_string = "host='192.168.31.103' dbname='cache' user='postgres' password=''"
    conn = psycopg2.connect(conn_string)
    # print(command)
    try:
        with conn.cursor() as cursor:
            cursor.execute(command)
            # fetch = cursor.fetchall()
        # print('Successfully', fetch)
    except psycopg2.Error as e:
        print("Exception: {}".format(e))
        raise SystemExit(e)
    finally:
        # print("finally")
        conn.commit()
        conn.close()


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


# file = "data/cachedb_dump.json"
# from_json(file)


file = "data/titles.txt"
data_set = from_file(file)

sql = "DROP TABLE IF EXISTS public.titles"
conn_psql(sql)

sql = "CREATE TABLE public.titles ( id character varying(20) PRIMARY KEY, name character varying(200) NOT NULL )"
conn_psql(sql)

for item in data_set:
    sql = "INSERT INTO public.titles(id, name) VALUES ('{}', '{}');".format(item['key'], item['name'])
    conn_psql(sql)
