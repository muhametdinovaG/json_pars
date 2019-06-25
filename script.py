#!/usr/bin/env python3
import datetime
import json
import os
import socket
import urllib.parse
import sqlite3
import hashlib

from collections import OrderedDict


# Создать таблицу если не создана
# CREATE TABLE hash (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, hash TEXT NOT NULL);

def get_id(name, url_video, url_poster):
    """
    Получение ID
    """
    data_str = name + url_video + url_poster
    m = hashlib.md5()
    m.update(data_str.encode('utf-8'))
    hash = m.hexdigest()
    q = "SELECT * FROM hash where hash = ?"
    cur.execute(q, [hash])
    row = cur.fetchone()
    if row is None:
        cur.execute("INSERT INTO hash (hash) VALUES (?)", [hash])
        conn.commit()
    cur.execute(q, [hash])
    row = cur.fetchone()
    if row:
        return row[0]
    else:
        return 0


def get_duration(path):
    """
    Получение продолжительности
    """
    try:
        return int(open(path + '/' + 'Продолжительность.txt', 'r', encoding='WINDOWS-1251').read().strip())
    except:
        return ''


def get_coutry(path):
    """
    Получение страны
    """
    try:
        return open(path + '/' + 'Страна выпуска.txt', 'r', encoding='WINDOWS-1251').read().strip()
    except:
        return ''


def get_year(path):
    """
    Получение года выпуска
    """
    try:
        return int(open(path + '/' + 'Год.txt', 'r', encoding='WINDOWS-1251').read().strip())
    except:
        return ''


def get_description(path):
    """
    Получение описания
    """
    try:
        return open(path + '/' + 'Описание.txt', 'r', encoding='WINDOWS-1251').read().strip()
    except:
        return ''


def get_genres(path):
    """
    Получение жанров
    """
    try:
        return open(path + '/' + 'Жанры.txt', 'r', encoding='WINDOWS-1251').read().strip().split(', ')
    except:
        return []


def get_rating(path):
    """
    Получение возрастного рейтинга
    """
    try:
        return int(open(path + '/' + 'Возрастной рейтинг.txt', 'r', encoding='WINDOWS-1251').read().strip())
    except:
        return ''


def get_seria(path):
    """
    Получение информации о сезоне и серии
    """
    try:
        return int(open(path + '/' + 'Сезон и серия.txt', 'r', encoding='WINDOWS-1251').read().strip())
    except:
        return ''


def get_poster_file_path(path):
    """
    Получение пути до файла постер
    """
    file_path = ''
    try:
        for file in os.listdir(path):
            if file.endswith(".jpg") or file.endswith(".png"):
                file_path = os.path.join(path, file)
    except:
        pass
    return file_path


def get_video_file_path(path):
    """
    Получение пути до файла видео
    """
    file_path = ''
    try:
        for file in os.listdir(path):
            if file.endswith(".MP4") or file.endswith(".mp4") or file.endswith(".wmv"):
                file_path = os.path.join(path, file)
    except:
        pass
    return file_path


def get_address_url(path, file_path):
    """
    Генерация url
    """
    if file_path == '':
        return ''
    try:
        return 'http://' + socket.gethostbyaddr(socket.gethostname())[0] + (
            urllib.parse.quote(file_path.replace(path, '')))
    except:
        return ''


def get_last_update(file_path):
    """
    Время создания изменения файла
    """
    try:
        return datetime.datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%dT%H:%M:%S%z')
    except:
        return ''


# Конект к бд
conn = sqlite3.connect('json24tv.db')

cur = conn.cursor()

# Путь к просмтриваемым каталогам
path = os.path.dirname(os.path.realpath(__file__)) + '/www'

root = os.listdir(path)

tree = OrderedDict()

path_ex = ''

# Корень
for r in root:
    path_root = "{}/{}".format(path, r)

    if not os.path.isdir(path_root):
        continue

    categories = os.listdir(path_root)

    # Категории
    for category in categories:

        path_category = "{}/{}".format(path_root, category)

        if not os.path.isdir(path_category):
            continue

        programs = os.listdir(path_category)

        # Программы
        for program in programs:

            path_program = "{}/{}".format(path_category, program)

            if not os.path.isdir(path_program):
                continue

            poster_file_path = get_poster_file_path(path_program)
            video_file_path = get_video_file_path(path_program)
            tree.setdefault(program, {
                'id': get_id(program, get_video_file_path(path_program), get_address_url(path, poster_file_path)),
                'title': program,
                'duration': get_duration(path_program),
                'country': get_coutry(path_program),
                'year': get_year(path_program),
                'url_poster': get_address_url(path, poster_file_path),
                'video_url': get_address_url(path, video_file_path),
                'description': get_description(path_program),
                'genre': get_genres(path_program),
                'age': get_rating(path_program),
                'last_update': get_last_update(poster_file_path),
                'category': category,
            })

            # Серии
            series = os.listdir(path_program)
            for seria in series:
                path_seria = "{}/{}".format(path_program, seria)
                if not os.path.isdir(path_seria):
                    continue

                poster_file_path = get_poster_file_path(path_seria)
                video_file_path = get_video_file_path(path_seria)

                if 'series' not in tree[program]:
                    tree[program].update({
                        'series': []
                    })

                tree[program]['series'].append({
                    'id': get_id(program, get_address_url(path, video_file_path),
                                 get_address_url(path, poster_file_path)),
                    'title': seria,
                    'duration': get_duration(path_seria),
                    'country': get_coutry(path_seria),
                    'year': get_year(path_seria),
                    'description': get_description(path_seria),
                    'genre': get_genres(path_seria),
                    'age': get_rating(path_seria),
                    'seria': get_seria(path_seria),
                    'video_url': get_address_url(path, video_file_path),
                    'url_poster': get_address_url(path, poster_file_path),
                    'last_update': get_last_update(video_file_path)
                })
            if 'series' in tree[program]:
                if len(tree[program]['series']) == 1:
                    tree[program].update(tree[program]['series'][0])
                    tree[program].pop('series', None)
                elif len(tree[program]['series']) > 1:
                    for n in range(len(tree[program]['series'])):
                        tree[program]['series'][n].update({
                            'season': 1
                        })

# Группировка по категориям
tree_result = {}
for program in tree.values():
    category = program['category']
    if category not in tree_result:
        tree_result.setdefault(category, [])
    program.pop('category', None)
    tree_result[category].append(program)

# Генерация json
result = json.dumps(tree_result)

# Сохранения json в файл
fs = open(path + '/template.json', 'w')
fs.write(result)
fs.close()

# Закрытие конекта к бд
cur.close()
conn.close()
