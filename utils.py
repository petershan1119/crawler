import re
import os
import requests
from bs4 import BeautifulSoup

def get_top100_list(refresh_html=False):

    root_dir = os.path.dirname(os.path.abspath(__name__))
    path_data_dir = os.path.join(root_dir, 'data')
    url_chart_realtime = 'https://www.melon.com/chart/index.htm'


    if not os.path.isdir(path_data_dir):
        os.mkdir(path_data_dir)

    file_path = os.path.join(path_data_dir, 'chart_realtime.html')

    if not os.path.isfile(file_path) or refresh_html is True:
        with open(file_path, 'wt') as f:
            response = requests.get(url_chart_realtime)
            source = response.text
            f.write(source)


    # file_path = os.path.join(path_data_dir, 'chart_realtime_50.html')
    # try:
    #     file_mode = 'wt' if refresh_html else 'xt'
    #     with open(file_path, file_mode) as f:
    #         response = requests.get(url_chart_realtime_50)
    #         source = response.text
    #         f.write(source)
    # except FileExistsError:
    #     print(f'"{file_path}" file is already exists!')

    source = open(file_path, 'rt').read()
    soup = BeautifulSoup(source, 'lxml')

    result = []
    for tr in soup.find_all('tr', class_=['lst50', 'lst100']):
        rank = tr.find('span', class_='rank').text
        title = tr.find('div', class_='rank01').find('a').text
        artist = tr.find('div', class_='rank02').find('a').text
        album = tr.find('div', class_='rank03').find('a').text
        url_img_cover = tr.find('a', class_='image_typeAll').find('img').get('src')
        # http://cdnimg.melon.co.kr/cm/album/images/101/28/855/10128855_500.jpg/melon/resize/120/quality/80/optimize
        # .* -> 임의 문자의 최대 반복
        # \. -> '.' 문자
        # .*?/ -> '/'이 나오기 전까지의 최소 반복
        p = re.compile(r'(.*\..*?)/')
        url_img_cover = re.search(p, url_img_cover).group(1)

        result.append({
            'rank': rank,
            'title': title,
            'url_img_cover': url_img_cover,
            'artist': artist,
            'album': album,
        })

    return result
