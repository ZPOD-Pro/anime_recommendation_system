import os
import csv
import time
from concurrent.futures import ThreadPoolExecutor
import requests
import pandas as pd
from bs4 import BeautifulSoup


COMMENT_LIST = "https://bangumi.tv/subject/{id_}/comments?page={page}"
HEADER = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/91.0.4472.101 Safari/537.36 "
}


def parse_comment(html):
    """
    迭代器
    解析吐槽信息并返回，若到评论末尾则返回False
    :param html:传入吐槽页
    :return 吐槽信息元组
    """
    soup = BeautifulSoup(html, 'lxml')
    divs = soup.find_all('div', class_='text')
    if len(divs) == 0:
        yield False
        return
    for t in divs:
        ta = t.a
        user_id = ta['href'][6:]
        user_name = ta.text
        rating = t.span.span['class'][1][5:] if t.span else ""
        comment = t.p.text if t.p else ""
        item = (user_id, user_name, rating, comment)
        yield item


def get_page(anime_id, page):
    """
    获取网页
    :param anime_id: 动漫id
    :param page: 翻页
    :return: html页面
    """
    url = COMMENT_LIST.format(id_=anime_id, page=page)
    try:
        time.sleep(1)
        res = requests.get(url, headers=HEADER)
        # res.encoding = res.apparent_encoding
        res.encoding = 'utf8'
        html = res.text
        return html
    except Exception as e:
        print(e)
        time.sleep(5)
        return get_page(anime_id, page)


def anime_comments(anime_id, name):
    """
    获取动画评论
    :param anime_id:
    """
    page = 1
    p = ThreadPoolExecutor(6)
    is_end = False
    while not is_end:
        future = p.submit(run, anime_id, name, page)
        is_end = future.result()
        page += 1


def write_csv(item, filename):
    """
    将条目写入csv文件
    """
    with open(filename, 'a+', encoding='utf-8', newline="") as cf:
        wt = csv.writer(cf, quoting=csv.QUOTE_MINIMAL)
        wt.writerow(item)
    print(*item)


def run(anime_id, anime_name, page):
    """
    处理一个动画吐槽页
    """
    html = get_page(anime_id, page)
    for item in parse_comment(html):
        if not item:
            # 没数据了，表示已到评论末尾
            return True
        user_id, user_name, rating, comment = item
        data = user_id, user_name, anime_id, anime_name, rating, comment
        write_csv(data, "comment1.csv")
    return False


def main():
    table_head = ['name', 'other_name', 'rank', 'rating']
    an_list = pd.read_csv('animelistWEB.csv', names=table_head)
    for aid in an_list.index:
        name = an_list['name'][aid]
        print(name)
        anime_comments(aid, name)


if __name__ == '__main__':
    main()
    os.system('pause')
