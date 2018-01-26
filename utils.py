import os
import re

import requests
from bs4 import BeautifulSoup


def get_top100_list(refresh_html=False):
    """
    실시간 차트 1~100위의 리스트 반환
    파일위치:
        data/chart_realtime.html
    :param refresh_html: True일 경우, 무조건 새 HTML파일을 사이트에서 받아와 덮어씀
    :return: 곡 정보 dict의 list
    """
    # utils가 있는
    path_module = os.path.abspath(__file__)
    print(f'path_module: \n{path_module}')

    # 프로젝트 컨테이너 폴더 경로
    root_dir = os.path.dirname(path_module)
    print(f'root_dir: \n{root_dir}')

    # data/ 폴더 경로
    path_data_dir = os.path.join(root_dir, 'data')
    print(f'path_data_dir: \n{path_data_dir}')

    # 만약에 path_data_dir에 해당하는 폴더가 없을 경우 생성해준다
    os.makedirs(path_data_dir, exist_ok=True)

    # 실시간 1~100위 웹페이지 주소
    url_chart_realtime = 'https://www.melon.com/chart/index.htm'

    # 실시간 1~100위 웹페이지 HTML을 data/chart_realtime.html 에 저장
    file_path = os.path.join(path_data_dir, 'chart_realtime.html')
    try:
        # refresh_html매개변수가 True일 경우, wt모드로 파일을 열어 새로 파일을 다운받도록 함
        file_mode = 'wt' if refresh_html else 'xt'
        with open(file_path, file_mode) as f:
            response = requests.get(url_chart_realtime)
            source = response.text
            f.write(source)
    # xt모드에서 있는 파일을 열려고 한 경우 발생하는 예외
    except FileExistsError:
        print(f'"{file_path}" file is already exists!')

    # if not os.path.isdir(path_data_dir):
    #     os.mkdir(path_data_dir)
    #
    # file_path = os.path.join(path_data_dir, 'chart_realtime.html')
    #
    # if not os.path.isfile(file_path) or refresh_html is True:
    #     with open(file_path, 'wt') as f:
    #         response = requests.get(url_chart_realtime)
    #         source = response.text
    #         f.write(source)

    # 1. source변수에 위에 정의해놓은 file_path(data/chart_realtime.html)의
    #       파일 내용을 읽어온 결과를 할당
    f = open(file_path, 'rt', encoding='utf8')
    source = f.read()
    f.close()
    # 2. soup변수에 BeautifulSoup클래스 호출에 source를 전달해 만들어진 인스턴스를 할당
    #    soup = BeautifulSoup(source)
    soup = BeautifulSoup(source, 'lxml')
    # 3. BeautifulSoup을 사용해 HTML을 탐색하며 dict의 리스트를(result) 생성, 마지막에 리턴

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
        song_id = tr['data-song-no']

        result.append({
            'rank': rank,
            'title': title,
            'url_img_cover': url_img_cover,
            'artist': artist,
            'album': album,
            'song_id': song_id
        })
    return result


def get_song_detail(song_id):
    """
    song_id에 해당하는 곡 정보 dict를 반환
    위의 get_top100_list의 각 곡 정보에도 song_id가 들어가도록 추가
    http://www.melon.com/song/detail.htm?songId=30755375
    위 링크를 참조
    파일명
        song_detail_{song_id}.html
    :param song_id: 곡 정보 dict
    :return:
    """
    path_module = os.path.abspath(__file__)
    root_dir = os.path.dirname(path_module)
    path_data_dir = os.path.join(root_dir, 'data/songs')
    os.makedirs(path_data_dir, exist_ok=True)

    url_song_id_common = 'https://www.melon.com/song/detail.htm?songId='
    url_song_id_each = url_song_id_common + str(song_id)

    file_path = os.path.join(path_data_dir, '{}.html'.format(str(song_id)))

    try:
        with open(file_path, 'wt', encoding="utf8") as f:
            response = requests.get(url_song_id_each)
            source = response.text
            f.write(source)
    except FileExistsError:
        print(f'"{file_path}" file is already exists!')

    f = open(file_path, 'rt', encoding='utf8')
    source = f.read()
    f.close()

    soup = BeautifulSoup(source, 'lxml')

    song_title = soup.find('div', class_='song_name').text[3:].strip()
    song_artist = soup.find('div', class_='artist').text.strip()

    song_meta = soup.find('div', class_='meta')
    song_meta_dt = song_meta.find_all('dt')

    song_album = song_meta_dt[0].next_sibling.next_sibling.find('a').text
    song_release_date = song_meta_dt[1].next_sibling.next_sibling.text
    song_genre = song_meta_dt[2].next_sibling.next_sibling.text
    song_flac = song_meta_dt[3].next_sibling.next_sibling.text

    song_lyrics = soup.find('div', class_='lyric').text.strip()

    prdcr = soup.find('div', class_='section_prdcr')

    if prdcr:
        song_prdrc_dict = {}
        for entry in soup.find('div', class_='section_prdcr').find_all('div', class_='entry'):
            entry_name = entry.find('a').text
            entry_type = entry.find(class_='type').text
            song_prdrc_dict.setdefault(entry_type, [])
            song_prdrc_dict[entry_type].append(entry_name)
    else:
        song_prdrc_dict = {}

    result = []
    result.append({
        'song_id': song_id,
        'song_title': song_title,
        'song_artist': song_artist,
        'song_album': song_album,
        'song_release_date': song_release_date,
        'song_genre': song_genre,
        'song_flac': song_flac,
        'song_lyrics': song_lyrics,
    })

    result[0].update(song_prdrc_dict)

    return result
