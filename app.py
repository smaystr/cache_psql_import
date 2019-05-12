from database import Database, ConnectionCursor
import json

# import warnings
# import re
# from sqlalchemy import create_engine

# warnings.simplefilter('ignore')

# Database.set_connection(host='192.168.31.103', database='cache', user='postgres', password='')

Database.set_connection(host='localhost', database='cache', user='postgres', password='postgres')
# Database.set_connection(host='localhost', database='kais', user='postgres', password='postgres')


def fix_json(filename):

    files = []
    objects_per_file = 10000
    count = 0
    with open(filename, encoding='cp1251', errors='ignore') as f:

        newline = f.readline()
        small_filename = filename[:filename.rindex('.')] + '_{}.txt'.format(count + objects_per_file)
        files.append(small_filename)
        smallfile = open(small_filename, "w")
        count = 0
        new_file = False

        for line in f:
            if newline == '},\n' or newline == '}\n':
                count += 1
                if count % objects_per_file == 0 or line == '}\n':
                    smallfile.write('}\n')
                    smallfile.write('}\n')
                    smallfile.close()
                    if line == '}\n':
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


def check_data():
    filename = "check3.txt"
    with ConnectionCursor() as cursor:
        cursor.execute("SELECT d1.id, d1.article_id, d1.field_value, d2.id, "
                       "d2.field_value, d3.field_value from data d1 "
                       "LEFT JOIN data d2 ON d1.article_id = d2.article_id AND d2.title_id = '2,0,a,ru' "
                       "LEFT JOIN data d3 ON d1.article_id = d3.article_id AND d3.title_id = '3,30,a,ang' "
                       "WHERE d1.title_id='7,0,ru' AND LENGTH(d1.field_value) > 63 ORDER BY d1.article_id")
        records = cursor.fetchall()
        n = 0
        with open(filename, "w") as f:
            f.write("rid|article_id|field_value1|field_value2|field_value3\n")

            for row in records:
                field_value = row[2]

                if field_value.find('. ') > 0 and not field_value.split(None, 1)[1][:1].isupper():
                    f.write(str(row[0]) + '|' + str(row[1]) + '|' + str(field_value) +
                            "|" + str(row[3]) + "|" + str(row[4]) + "|" + str(row[5]) + "\n")
                    # print(str(rid) + '|' + field_value.split(None, 1)[1][:1])
                    n += 1

                # new_value = field_value
                # first_del_pos = new_value.find("<")  # get the position of <
                # while first_del_pos > 0:
                #     second_del_pos = new_value.find(">")  # get the position of >
                #     if second_del_pos < len(new_value)-1:
                #         if new_value[first_del_pos-1] == ' ' and new_value[second_del_pos+1] == ' ':
                #             first_del_pos -= 1
                #     new_value = new_value.replace(new_value[first_del_pos:second_del_pos+1], '')
                #     first_del_pos = new_value.find("<")  # get the position of <
                #
                # cursor.execute("UPDATE data SET field_value=%s WHERE id=%s", (new_value, rid))
                # updated_rows = cursor.rowcount
                # print(str(updated_rows) + " rows updated|" + str(rid) + '|' + str(field_value) + ' -> ' + str(new_value))
                # # print(str(rid) + '|' + str(field_value) + ' -> ' + str(new_value))
                # n += updated_rows

    print(str(n) + " rows printed out")


def export_data():
    filename = "export_auth.txt"
    i = 0

    with ConnectionCursor() as cursor:
        cursor.execute("SELECT d1.article_id, d2.field_value, d3.field_value, d4.field_value FROM data d1 "
                       "LEFT JOIN data d2 ON d1.article_id = d2.article_id AND d2.title_id = '7,0' "
                       "LEFT JOIN data d3 ON d1.article_id = d3.article_id AND d3.title_id = '7,0,ang' "
                       "LEFT JOIN data d4 ON d1.article_id = d4.article_id AND d4.title_id = '7,0,ru' "
                       "WHERE d1.title_id = '2,0,a' ORDER BY d1.article_id")
        records = cursor.fetchall()
        with open(filename, "w") as f:
            f.write("article_id\tfield_value1\tcount1\tfield_value2\tcount2\tfield_value3\tcount3\n")
            for row in records:
                article_id = row[0]
                field_value1 = row[1]
                field_value2 = row[2]
                field_value3 = row[3]

                count1 = 0
                count2 = 0
                count3 = 0
                if row[1] is not None:
                    count1 = field_value1.count(',') + 1
                if row[2] is not None:
                    count2 = field_value2.count(',') + 1
                if row[3] is not None:
                    count3 = field_value3.count(',') + 1

                f.write(str(row[0]) + "\t" + str(row[1]) + "\t" + str(count1) + "\t" +
                        str(row[2]) + "\t" + str(count2) + "\t" + str(row[3]) + "\t" + str(count3) + "\n")
                i += 1

    print("Обработано {} записей. Последняя обработанная запись № {}".format(i, article_id))


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
    with open(filename, encoding='cp1251') as f:
        content = f.read().splitlines()
        for line in content:
            row_data = line.split("\t")
            row = {'f1': row_data[0],
                   'f2': row_data[1],
                   'f3': row_data[2],
                   'f4': row_data[3]
                   }
            data.append(row)

    return data


def import_data():
    filename = "pub3.txt"
    data_set = from_file(filename)
    inserted_rows = 0
    skipped_rows = 0

    with ConnectionCursor() as cursor:
        for item in data_set:
            if item['f2'] == "None":
                item['f2'] = ""
            if item['f3'] == "None":
                item['f3'] = ""
            if item['f4'] == "None":
                item['f4'] = ""

            if (item['f2'] != "") or (item['f3'] != "") or (item['f4'] != ""):
                cursor.execute('INSERT INTO public."publication-lang"("publication-id_publications", '
                               '"language-id_languages", "pub-lang-title", "abstract-lang", "authors-lang") '
                               'VALUES (%s, %s, %s, %s, %s)',
                               (item['f1'], "9", item['f2'], item['f3'], item['f4']))
                inserted_rows += cursor.rowcount
                # print(str(cursor.rowcount) + " rows updated")
            else:
                print("row " + str(item['f1']) + " skipped")
                skipped_rows += 1

    print(str(inserted_rows) + " rows TOTAL inserted")
    print(str(skipped_rows) + " rows TOTAL skipped")
    print(str(inserted_rows+skipped_rows) + " rows IN TOTAL")


def update_data_table():
    filename = "export31.txt"
    data_set = from_file(filename)
    updated_rows = 0
    with ConnectionCursor() as cursor:
        for item in data_set:
            # cursor.execute("UPDATE data SET field_value=%s WHERE article_id=%s AND title_id='7,0,ru'",
            #                (item['name'], item['key']))
            cursor.execute("UPDATE data SET field_value=%s WHERE id=%s",
                           (item['name'], item['key']))
            updated_rows += cursor.rowcount
            print(str(cursor.rowcount) + " rows updated")

    print(str(updated_rows) + " rows TOTAL updated")


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
        selection = input("1. Fix and split json file, DROP and CREATE 'data' table from resulting json files.\n"
                          "2. Export data.\n"
                          "3. Analise.\n"
                          "4. Import data.\n"
                          "5. Quit.\n"
                          "Enter your selection: ")
        if selection == '1':
            file = "data/datan.txt"
            files = fix_json(file)
            print(files)
            from_json(files, True)
        elif selection == '2':
            export_data()
        elif selection == '3':
            check_data()
        elif selection == '4':
            import_data()
        elif selection == '5':
            return


main()
