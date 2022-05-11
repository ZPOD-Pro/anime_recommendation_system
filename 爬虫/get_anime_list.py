import csv
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor
import requests
from bs4 import BeautifulSoup

HEADER = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/91.0.4472.101 Safari/537.36 "
}
ANIME_LIST = "https://bangumi.tv/anime/browser/tv/?sort=rank&page={page}"


def find_num(text):
    return int(re.search("\d+", text).group())


def parse_page(html):
    soup = BeautifulSoup(html, 'lxml')
    divs = soup.find_all("div", class_="inner")[1:-1]
    for t in divs:
        pt = t.find('p', class_='info tip')
        num = find_num(pt.text)
        if num < 3:
            continue
        at = t.find('a', class_='l')
        bgm_id = find_num(at['href'])
        name = at.text
        small = t.find('small', class_='grey')
        jp_name = small.text if small else ""
        rank = find_num(t.find('span').text)
        score = t.find('small', class_='fade').text
        item = (bgm_id, name, jp_name, rank, score)
        yield item


def get_page(page):
    url = ANIME_LIST.format(page=page)
    try:
        time.sleep(1)
        res = requests.get(url, headers=HEADER)
        res.encoding = res.apparent_encoding
        html = res.text
        return html
    except Exception as e:
        print(e)
        time.sleep(5)
        return get_page(page)


def write_csv(item, filename):
    with open(filename, 'a+', encoding='utf-8', newline="") as cf:
        wt = csv.writer(cf, quoting=csv.QUOTE_MINIMAL)
        wt.writerow(item)
    print(*item)


def run(page):
    html = get_page(page)
    data = parse_page(html)
    for item in data:
        write_csv(item, "animelist.csv")


def main():
    p = ThreadPoolExecutor(6)
    for i in range(1, 23):
        p.submit(run, i)


if __name__ == '__main__':
    main()
    os.system("pause")
