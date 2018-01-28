import os
import re
import requests
from bs4 import BeautifulSoup, NavigableString

PATH_MODULE = os.path.abspath(__file__)
#PATH_MODULE = '/Users/sangwonhan/projects/crawler/utils_r/models_hw.py'
ROOT_DIR = os.path.dirname(os.path.dirname(PATH_MODULE))
DATA_DIR = os.path.join(ROOT_DIR, 'data')


class MelonCrawler:
    def search_song(self, q):
        url = 'https://www.melon.com/search/song/index.htm'
        params = {
            'q': q,
            'section': 'song'
        }
        response = requests.get(url, params)
        soup = BeautifulSoup(response.text, 'lxml')
        tr_list = soup.select('form#frm_defaultList table > tbody > tr')

        result = []
        for tr in tr_list:
            song_id = tr.select_one('td:nth-of-type(1) input[type=checkbox]').get('value')
            title = tr.select_one('td:nth-of-type(3) a.fc_gray').get_text(strip=True)
            artist = tr.select_one('td:nth-of-type(4) span.checkEllipsisSongdefaultList').get_text(strip=True)
            album = tr.select_one('td:nth-of-type(5) a').get_text(strip=True)

            song = Song(song_id=song_id, title=title, artist=artist, album=album)
            result.append(song)
        return result

    def search_artist(self, q):
        url = 'https://www.melon.com/search/artist/index.htm'
        params = {
            'q': q,
            'section': '',
            'searchGnbYn': 'Y',
            'kkoSpl': 'N',
            'kkoDpType': '',
            'ipth': 'srch_form',
        }
        response = requests.get(url, params)
        soup = BeautifulSoup(response.text, 'lxml')

        pagelist_li = soup.select('div#pageList ul > li')
        result = []
        for item in pagelist_li:
            artist_id = item.select_one('button').get('data-artist-no')
            artist = item.select_one('a.ellipsis').get_text(strip=True)
            nation_gender_solo = item.select_one('dd.gubun').get_text(strip=True)
            # nation, gender, solo_group = item.select_one('dd.gubun').get_text(strip=True).split('/')
            genre = item.select_one('div.fc_strong').get_text(strip=True).split(',')
            url_img_cover_raw = item.select_one('img').get('src')
            url_match = re.search(r'http://.*?\.jpg', url_img_cover_raw)
            if url_match:
                url_img_cover = url_match.group()
            else:
                url_img_cover = ''

            artist = Artist(artist_id=artist_id, artist=artist, nation_gender_solo=nation_gender_solo,
                            genre=genre, url_img_cover=url_img_cover)
            result.append(artist)

            # result.append({
            #     'artist_id': artist_id,
            #     'artist': artist,
            #     'nation_gender_solo': nation_gender_solo,
            #     # 'nation': nation,
            #     # 'gender': gender,
            #     # 'solo_group': solo_group,
            #     'genre': genre,
            #     'url_img_cover': url_img_cover,
            # })
        return result


class Song:
    def __init__(self, song_id, title, artist, album):
        self.song_id = song_id
        self.title = title
        self.artist = artist
        self.album = album

        self._release_date = None
        self._lyrics = None
        self._genre = None
        self._producers = None

    def __str__(self):
        return f'{self.title} (아티스트: {self.artist}, 앨범: {self.album}'

    def get_detail(self, refresh_html=False):
        file_path = os.path.join(DATA_DIR, 'songs', f'song_detail_{self.song_id}.html')
        try:
            file_mode = 'wt' if refresh_html else 'xt'
            with open(file_path, file_mode, encoding='utf8') as f:
                url = 'https://www.melon.com/song/detail.htm'
                params = {
                    'songId': self.song_id,
                }
                response = requests.get(url, params)
                source = response.text
                file_length = f.write(source)
                if file_length < 10:
                    raise ValueError('파일이 너무 짧습니다!')
        except FileExistsError:
            print(f'"{file_path}" file is already exists!')
        except ValueError:
            os.remove(file_path)
            return

        source = open(file_path, 'rt', encoding='utf8').read()
        soup = BeautifulSoup(source, 'lxml')

        div_entry = soup.find('div', class_='entry')
        # title = div_entry.find('div', class_='song_name').strong.next_sibling.strip()
        # artist = div_entry.find('div', class_='artist').get_text(strip=True)
        dl = div_entry.find('div', class_='meta').find('dl')
        items = [item.get_text(strip=True) for item in dl.contents if not isinstance(item, str)]
        it = iter(items)
        description_dict = dict(zip(it, it))

        # album = description_dict.get('앨범')
        release_date = description_dict.get('발매일')
        genre = description_dict.get('장르')

        div_lyrics = soup.find('div', id='d_video_summary')

        lyrics_list = []
        for item in div_lyrics:
            if item.name == 'br':
                lyrics_list.append('\n')
            elif type(item) is NavigableString:
                lyrics_list.append(item.strip())
        lyrics = ''.join(lyrics_list)

        prdcr = soup.find('div', class_='section_prdcr')

        if prdcr:
            producers = {}
            for entry in soup.find('div', class_='section_prdcr').find_all('div', class_='entry'):
                entry_name = entry.find('a').text
                entry_type = entry.find(class_='type').text
                producers.setdefault(entry_type, [])
                producers[entry_type].append(entry_name)
        else:
            producers = {}

        # self.title = title
        # self.artist = artist
        # self.album = album
        self._release_date = release_date
        self._genre = genre
        self._lyrics = lyrics
        self._producers = producers

    @property
    def release_date(self):
        if not self._release_date:
            self.get_detail()
        return self._release_date

    @property
    def genre(self):
        if not self._genre:
            self.get_detail()
        return self._genre

    @property
    def lyrics(self):
        if not self._lyrics:
            self.get_detail()
        return self._lyrics

    @property
    def producers(self):
        if not self._producers:
            self.get_detail()
        return self._producers


# class Artist:
#     def __init__(self, artist_id, name, url_img_cover):
#         self.artist_id = artist_id
#         self.name = name
#         self.url_img_cover = url_img_cover
#         self.real_name = None
#
#         self._info = {}
#         self._award_history = []
#         self._introduction = {}
#         self._activity_information = {}
#         self._personal_information = {}
#         self._related_information = {}
# "아티스트 채널" 바로 밑에 있는 대표정보 (dict)와
# 수상이력(list)
# 아티스트 소개(str)
# 활동정보(dict)
# 신상정보(dict)
# 연관정보(dict)


class Artist:
    def __init__(self, artist_id, artist, nation_gender_solo, genre, url_img_cover):
        self.artist_id = artist_id
        self.artist = artist
        self.nation_gender_solo = nation_gender_solo
        # self.nation = nation
        # self.gender = gender
        # self.solo_group = solo_group
        self.genre = genre
        self.url_img_cover = url_img_cover

        self._real_name = None
        self._info = {}
        self._award_history = []
        self._introduction = None
        self._activity_information = {}
        self._personal_information = {}
        self._related_information = {}

    def __str__(self):
        return f'{self.artist} (국적/성별/솔로: {self.nation_gender_solo}, 장르: {self.genre}'

    def get_detail(self, refresh_html=False):
        file_path = os.path.join(DATA_DIR, 'artists', f'artist_detail_{self.artist_id}.html')
        try:
            file_mode = 'wt' if refresh_html else 'xt'
            with open(file_path, file_mode, encoding='utf8') as f:
                url = 'https://www.melon.com/artist/detail.htm'
                params = {
                    'artistId': self.artist_id,
                }
                response = requests.get(url, params)
                source = response.text
                file_length = f.write(source)
                if file_length < 10:
                    raise ValueError('파일이 너무 짧습니다!')
        except FileExistsError:
            print(f'"{file_path}" file already exists!')
        except ValueError:
            os.remove(file_path)
            return

        source = open(file_path, 'rt', encoding='utf8').read()
        soup = BeautifulSoup(source, 'lxml')

        span_realname = soup.select_one('div.wrap_atist_info p.title_atist span.realname')
        if span_realname:
            real_name = soup.select_one('div.wrap_atist_info p.title_atist span.realname').get_text(strip=True).strip('()')
        else:
            real_name = ''

        atist_info_dt_raw = soup.select('div.wrap_atist_info dl.atist_info dt')
        atist_info_dd_raw = soup.select('div.wrap_atist_info dl.atist_info dd')
        atist_info_dt = [item.get_text(strip=True) for item in atist_info_dt_raw]
        atist_info_dd = []
        for item in atist_info_dd_raw:
            if item.select_one('span.gubun'):
                item = item.select_one('span.gubun')
            if item.select_one('span.ellipsis'):
                item = item.select_one('span.ellipsis')
            atist_info_dd.append(item.get_text(strip=True))
        info = dict(zip(atist_info_dt, atist_info_dd))

        award_history_dd = soup.select('div.section_atistinfo01 dd')
        if award_history_dd:
            award_history = [item.get_text(strip=True) for item in award_history_dd]
        else:
            award_history = []

        introduction_div = soup.select_one('div.section_atistinfo02 div.atist_insdc')
        if introduction_div:
            introduction_list = []
            for item in introduction_div:
                if item.name == 'br':
                    introduction_list.append('\n')
                elif type(item) is NavigableString:
                    introduction_list.append(item.strip())
            introduction = ''.join(introduction_list)
        else:
            introduction = ''

        activity_information_dt_raw = soup.select('div.section_atistinfo03 dl.list_define dt')
        activity_information_dd_raw = soup.select('div.section_atistinfo03 dl.list_define dd')
        if activity_information_dt_raw:
            activity_information_dt = [item.get_text(strip=True) for item in activity_information_dt_raw]
            activity_information_dd = [item.get_text(strip=True) for item in activity_information_dd_raw]
            activity_information = dict(zip(activity_information_dt, activity_information_dd))
        else:
            activity_information = {}

        personal_information_dt_raw = soup.select('div.section_atistinfo04 dl.list_define dt')
        personal_information_dd_raw = soup.select('div.section_atistinfo04 dl.list_define dd')
        if personal_information_dt_raw:
            personal_information_dt = [item.get_text(strip=True) for item in personal_information_dt_raw]
            personal_information_dd = [item.get_text(strip=True) for item in personal_information_dd_raw]
            personal_information = dict(zip(personal_information_dt, personal_information_dd))
        else:
            personal_information = {}

        related_information_dt_raw = soup.select('div.section_atistinfo05 dl dt')
        related_information_dd_raw = soup.select('div.section_atistinfo05 dl dd')
        if related_information_dt_raw:
            related_information_dt = [item.get_text(strip=True) for item in related_information_dt_raw]
            related_information_dd = []
            for item in related_information_dd_raw:
                if item.select('button'):
                    b_item_list = []
                    for b_item in item.select('button'):
                        sns_name = b_item.get_text(strip=True)
                        window_open = b_item.get('onclick')
                        sns_url = re.search(r"window\.open\('(.*?)'", window_open).group(1)
                        sns = sns_name + ' (' + sns_url + ')'
                        b_item_list.append(sns)
                    item = '\n'.join(b_item_list)
                if isinstance(item, str):
                    related_information_dd.append(item)
                else:
                    related_information_dd.append(item.get_text(strip=True))
            related_information = dict(zip(related_information_dt, related_information_dd))
        else:
            related_information = {}

        self._real_name = real_name
        self._info = info
        self._award_history = award_history
        self._introduction = introduction
        self._activity_information = activity_information
        self._personal_information = personal_information
        self._related_information = related_information

    @property
    def real_name(self):
        if not self._real_name:
            self.get_detail()
        return self._real_name

    @property
    def info(self):
        if not self._info:
            self.get_detail()
        return self._info

    @property
    def award_history(self):
        if not self._award_history:
            self.get_detail()
        return self._award_history

    @property
    def introduction(self):
        if not self._introduction:
            self.get_detail()
        return self._introduction

    @property
    def activity_information(self):
        if not self._activity_information:
            self.get_detail()
        return self._activity_information

    @property
    def personal_information(self):
        if not self._personal_information:
            self.get_detail()
        return self._personal_information

    @property
    def related_information(self):
        if not self._related_information:
            self.get_detail()
        return self._related_information

    def get_songs(self, refresh_html=False):
        file_path = os.path.join(DATA_DIR, 'artist_song_list', f'artist_song_list_{self.artist_id}.html')

        try:
            file_mode = 'wt' if refresh_html else 'xt'
            with open(file_path, file_mode, encoding='utf8') as f:
                url = 'https://www.melon.com/artist/song.htm'
                params = {
                    'artistId': self.artist_id,
                }
                response = requests.get(url, params)
                source = response.text
                file_length = f.write(source)
                if file_length < 10:
                    raise ValueError('파일이 너무 짧습니다!')
        except FileExistsError:
            print(f'"{file_path}" file already exists!')
        except ValueError:
            os.remove(file_path)
            return

        source = open(file_path, 'rt', encoding='utf8').read()
        soup = BeautifulSoup(source, 'lxml')

        tr_list = soup.select('form#frm table > tbody > tr')

        result = []
        for tr in tr_list:
            if tr.select_one('td:nth-of-type(1) input[type=checkbox]'):
                song_id = tr.select_one('td:nth-of-type(1) input[type=checkbox]').get('value')
                title_a = tr.select_one('td:nth-of-type(3)').a
                title_exist = [item in ['fc_gray', 'btn'] for item in title_a.get('class')]
                if sum(title_exist) > 0:
                    title = title_a.get_text(strip=True)
                else:
                    title = ''
                # title = tr.select_one('td:nth-of-type(3) a.fc_gray').get_text(strip=True)
                artist = tr.select_one('td:nth-of-type(4) span.checkEllipsis').get_text(strip=True)
                album = tr.select_one('td:nth-of-type(5) a').get_text(strip=True)
            else:
                song_id = ''
                title = ''
                artist = ''
                album = ''

            result.append({
                'song_id': song_id,
                'title': title,
                'artist': artist,
                'album': album,
            })

        return result