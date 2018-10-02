# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup as bs
import requests
import sqlite3  # for dev db

import re
from time import sleep


# DB related
sqlite_file = 'common/train.sqlite3'  # same directory (for now)
table_name = 'training_data'
data_field = {'category': 'INTEGER', 'title': 'TEXT', 'document': 'TEXT'}

# website related
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/604.5.6 (KHTML, like Gecko) Version/11.0.3 Safari/604.5.6"}  # noqa
root_html = 'https://gunosy.com/'
categories = {
    1: 'エンタメ', 2: 'スポーツ',
    3: 'おもしろ', 4: '国内', 5: '海外',
    6: 'コラム', 7: 'IT・科学', 8: 'グルメ'}
categories_en = {
    1: 'Entertainment', 2: 'Sports',
    3: 'Funny/Cute', 4: 'Local', 5: 'Worldwide', 
    6: 'LIT', 7: 'Tech/Science', 8: 'Food'}


def create_connection():
    """ create a database connection to the SQLite database """
    try:
        conn = sqlite3.connect(sqlite_file)
        return conn
    except Exception as e:
        print(e)
    return None


def create_table():
    """ create a new table to the db if it wasn't created """
    try:
        conn = create_connection()
        c = conn.cursor()
        
        c.execute('PRAGMA TABLE_INFO({})'.format(table_name))
        info = c.fetchall()
        
        # if the table is already created
        if not info:
            col_names = list(data_field.keys())
            col_types = list(data_field.values())
            sql = '''
            CREATE TABLE {tn} (
            {cn} {ct}, {hn} {ht}, {dn} {dt});
            '''.format(tn=table_name, 
                       cn=col_names[0], ct=col_types[0],
                       hn=col_names[1], ht=col_types[1],
                       dn=col_names[2], dt=col_types[2])
            
            # create new table
            c.execute(sql)
            conn.commit()
    except Exception as e:
        print(e)
    finally:
        conn.close()


def delete_data():
    """ delete data from table """
    try:
        sql = 'DELETE FROM {tn}'.format(tn=table_name)
        conn = create_connection()
        c = conn.cursor()
        
        c.execute(sql)
        conn.commit()
    except Exception as e:
        print(e)
    finally:
        conn.close()


def update_table(i, title, text):
    """ connect to the db and update table """
    try:
        col_names = list(data_field.keys())
        sql = '''
        INSERT INTO {tn} ({cn}, {hn}, {dn}) VALUES ('{cv}', '{hv}', '{dv}')
        '''.format(tn=table_name,
                   cn=col_names[0],
                   hn=col_names[1],
                   dn=col_names[2],
                   cv=i, hv=title, dv=text)
        conn = create_connection()
        c = conn.cursor()
        
        c.execute(sql)
        conn.commit()
    except Exception as e:
        print(e)
    finally:
        conn.close()


def get_category_data(cat):
    """ get all the rows for category in the database """
    try:
        col_names = list(data_field.keys())
        sql = '''
        SELECT * FROM {tn} WHERE {cn}={val}
        '''.format(tn=table_name,
                   cn=col_names[0],
                   val=str(cat))
        conn = create_connection()
        c = conn.cursor()
        
        c.execute(sql)
        all_rows = c.fetchall()
        return all_rows
    except Exception as e:
        print(e)
    finally:
        conn.close()


def get_obj_from_html(link):
    """ retrieve html and make it a beautifulsoup object """
    html = requests.get(link, timeout=30, headers=headers)
    obj = bs(html.text, 'html.parser')
    return obj


def get_links_for_pages(link):
    """ retrieve pagnation link for the category """
    # 5 pages for each category
    return [link + '?page=' + str(i) for i in range(1, 6)]


def get_title_doc_from_article(obj):
    """ from the bs object, return cleaned title and document texts """
    title = obj.find("h1", class_='article_header_title')
    title_text = clean_text(title.get_text())
    
    article = obj.find("div", class_='article')
    ps = article.find_all("p")
    texts = [clean_text(p.get_text()) for p in ps]
    text = ''.join(texts)
    
    return title_text, text


def get_article_links(obj):
    """ retrieve all of the links for articles in a page """
    content_list = obj.find_all("div", class_='list_content')
    return [div.find('a').get('href') for div in content_list]


def clean_text(text):
    """ clean japanese text inorder for storing in database """
    # FIXME: make the regex better!
    # probably select the characters that should be stored
    # i.e., 
    # kanji = [一-龥]
    # hiragana = [ぁ-ん]
    # katakana = [ァ-ン]
    text = re.sub(r'https?://[\w/:%#\$&\?\(\)~\.=\+\-…]+', "", text)
    text = re.sub(r'[!-/:-@[-_{-~]', "", text)  # remove 'special' char
    text = re.sub(r'[：-＠…“”‘’＇｀・※；：＆「」『』（）［］【】©◇♡☆▼■◆●‼︎♪―～]', " ", text)  # remove japanese 'special' char
    text = re.sub(r'　', " ", text)  # remove full width space
    text = re.sub(r'\t', " ", text)  # remove tab
    text = re.sub('\n', " ", text)  # remove new line
    return text


def clean_link(link):
    """
    formats the link and also returns None 
    when the link is not the article we want
    """
    # check if the link matches gunosy's articles link
    # should be like this https://gunosy.com/articles/aLrQM
    needed_part = 'articles'
    parts = link.split('/')
    try:
        index = parts.index(needed_part)
        article_id = parts[index + 1]
        new_link = root_html + needed_part + '/' + article_id
        return new_link
    except Exception as e:
        print(e)
        return None


def get_training_data():
    """ get data used for training and upload it to the database """
    # database
    delete_data()  # should not delete when you want to store more data
    create_table()
    
    print('Getting training data from these articles...')
    # loop for each category
    for i, _ in categories.items():
        category_html = root_html + "categories/" + str(i)
        # loop for each page 
        for page in get_links_for_pages(category_html):
            content_urls = get_article_links(get_obj_from_html(page))
            # there should be 20 urls for each page
            for url in content_urls:
                print(url)
                content = get_obj_from_html(url)
                title, doc = get_title_doc_from_article(content)
                # save data as [category, title, text]
                update_table(i, title, doc)
                # scraping manner
                sleep(1)


def get_testing_data(link):
    """ get gunosy article (title and document) based on url """
    try:
        obj = get_obj_from_html(link)
        title, doc = get_title_doc_from_article(obj)
        return title, doc
    except Exception as e:
        print(e)
        return None, None
