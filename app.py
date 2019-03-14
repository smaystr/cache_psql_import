from database import Database, ConnectionCursor
import json

# import warnings
# import re
# from sqlalchemy import create_engine

# warnings.simplefilter('ignore')

# Database.set_connection(host='192.168.31.103', database='cache', user='postgres', password='')
Database.set_connection(host='localhost', database='cache', user='postgres', password='postgres')


def fix_json(filename):

    files = []
    objects_per_file = 10000
    count = 0
    with open(filename, encoding='utf-8') as f:

        newline = f.readline()
        small_filename = filename[:filename.rindex('.')] + '_{}.txt'.format(count + objects_per_file)
        files.append(small_filename)
        smallfile = open(small_filename, "w")
        count = 0
        new_file = False

        for line in f:
            if (line.startswith('"') and len(line) > 3) or line.startswith('}'):
                if newline == '},\n' or newline == '}\n':
                    count += 1
                    if count % objects_per_file == 0:
                        smallfile.write('}\n')
                        smallfile.write('}\n')
                        smallfile.close()
                        if line == '}\n' or line == '}':
                            return files

                        small_filename = filename[:filename.rindex('.')] + '_{}.txt'.format(count + objects_per_file)
                        files.append(small_filename)
                        smallfile = open(small_filename, "w")
                        smallfile.write('{\n')
                        new_file = True

                if new_file:
                    new_file = False
                else:
                    smallfile.write(newline)

                # Take next line and remove non-printable characters
                newline = line.replace(chr(0x1f), ' ')         # 'US' (unit separator)
                newline = newline.replace(chr(0x06), '\\"')    # 'ACK' (Acknowledge)

            else:
                # Remove newline character and concatenate with next line
                newline = newline.replace('\n', '') + line

    return files


def import_data():
    Database.set_connection(host='localhost', database='kais', user='postgres', password='postgres')
    connstr = 'host=localhost dbname=cache user=postgres password=postgres'
    with ConnectionCursor() as cursor:
        cursor.execute("SELECT dblink_connect('cache', %s);", (connstr,))

        cursor.execute("SELECT dblink_disconnect('cache');")


def from_json(files, drop):

    if drop:
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

    for filename in files:
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

                    if i % 1000 == 0:
                        print("Обработано {} записей из файла {}".format(i, filename))


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
        cursor.execute('DROP TABLE IF EXISTS public.data')
        cursor.execute('DROP TABLE IF EXISTS public.titles')
        cursor.execute('CREATE TABLE public.titles ( '
                       'id character varying(20) PRIMARY KEY, '
                       'name character varying(200) NOT NULL )')
        for item in data_set:
            cursor.execute('INSERT INTO public.titles (id, name) VALUES (%s, %s)', (item['key'], item['name']))


def main():
    while True:
        selection = input("1. Drop and create 'title' table (WARNING! table 'data' also DROP).\n"
                          "2. Fix and split json file, DROP and CREATE 'data' table from resulting json files.\n"
                          "3. Fix and split json file, INSERT to 'data' table from resulting json files.\n"
                          "4. Import data.\n"
                          "5. Quit.\n"
                          "Enter your selection: ")
        if selection == '1':
            create_title_table()
        elif selection == '2':
            file = "data/d_utf.txt"
            files = fix_json(file)
            print(files)
            from_json(files, True)
        elif selection == '3':
            file = "data/datan.txt"
            files = fix_json(file)
            from_json(files, False)
        elif selection == '4':
            import_data()
        elif selection == '5':
            return


main()
