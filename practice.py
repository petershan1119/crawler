"""
숙제
(좋아요 개수는 하지마세요)
print(chart) 했을 때
[
    {'rank': 1, 'title': '다른사람을 사랑하고 있어', 'artist': '수지 (SUZY)', 'album': 'Faces of Love',}
    {'rank': 1, 'title': '다른사람을 사랑하고 있어', 'artist': '수지 (SUZY)', 'album': 'Faces of Love',}
    {'rank': 1, 'title': '다른사람을 사랑하고 있어', 'artist': '수지 (SUZY)', 'album': 'Faces of Love',}
    {'rank': 1, 'title': '다른사람을 사랑하고 있어', 'artist': '수지 (SUZY)', 'album': 'Faces of Love',}
    {'rank': 1, 'title': '다른사람을 사랑하고 있어', 'artist': '수지 (SUZY)', 'album': 'Faces of Love',}
    {'rank': 1, 'title': '다른사람을 사랑하고 있어', 'artist': '수지 (SUZY)', 'album': 'Faces of Love',}
    {'rank': 1, 'title': '다른사람을 사랑하고 있어', 'artist': '수지 (SUZY)', 'album': 'Faces of Love',}
    {'rank': 1, 'title': '다른사람을 사랑하고 있어', 'artist': '수지 (SUZY)', 'album': 'Faces of Love',}
]
이렇게 나오도록 나머지 정규표현식 구현을 완성
"""

import re
from itertools import *


source = open('melon.html', 'rt').read()

PATTERN_DIV_RANK01 = re.compile(r'<div class="ellipsis rank01">.*?</div>', re.DOTALL)
PATTERN_DIV_RANK02 = re.compile(r'<div class="ellipsis rank02">.*?</div>', re.DOTALL)
PATTERN_DIV_RANK03 = re.compile(r'<div class="ellipsis rank03">.*?</div>', re.DOTALL)
PATTERN_A_CONTENT = re.compile(r'<a.*?>(.*?)</a>')

# 1. 순위
rank_list = re.findall(r'(\d{1,3})</span><span class="none">위', source)

# 2. 타이틀
title_list = []
match_list01 = re.finditer(PATTERN_DIV_RANK01, source)
for match_div_rank01 in match_list01:
    div_rank01_content = match_div_rank01.group()
    match_title = re.search(PATTERN_A_CONTENT, div_rank01_content)
    title = match_title.group(1)
    title_list.append(title)

# 3. 아티스트
artist_list = []
match_list02 = re.finditer(PATTERN_DIV_RANK02, source)
for match_div_rank02 in match_list02:
    div_rank02_content = match_div_rank02.group()
    match_artist = re.search(PATTERN_A_CONTENT, div_rank02_content)
    artist = match_artist.group(1)
    artist_list.append(artist)

# 4. 앨범
album_list = []
match_list03 = re.finditer(PATTERN_DIV_RANK03, source)
for match_div_rank03 in match_list03:
    div_rank03_content = match_div_rank03.group()
    match_album = re.search(PATTERN_A_CONTENT, div_rank03_content)
    album = match_album.group(1)
    album_list.append(album)

# 5. list 내 dictionary로 만들기
final_zip = zip(rank_list, title_list, artist_list, album_list)

final_list = []
for item in final_zip:
    temp_dict = {}
    temp_dict['rank'] = int(item[0])
    temp_dict['title'] = item[1]
    temp_dict['artist'] = item[2]
    temp_dict['album'] = item[3]
    final_list.append(temp_dict)

