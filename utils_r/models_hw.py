import os
import requests
from bs4 import BeautifulSoup, NavigableString

PATH_MODULE = os.path.abspath(__file__)
#PATH_MODULE = '/Users/sangwonhan/projects/crawler/utils_r'
#ROOT_DIR = os.path.dirname(PATH_MODULE)
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

            artist = Artist(artist_id=artist_id, artist=artist, nation_gender_solo=nation_gender_solo, genre=genre)
            result.append(artist)

            # result.append({
            #     'artist_id': artist_id,
            #     'artist': artist,
            #     'nation_gender_solo': nation_gender_solo,
            #     # 'nation': nation,
            #     # 'gender': gender,
            #     # 'solo_group': solo_group,
            #     'genre': genre,
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


class Artist:
    def __init__(self, artist_id, artist, nation_gender_solo, genre):
        self.artist_id = artist_id
        self.artist = artist
        self.nation_gender_solo = nation_gender_solo
        # self.nation = nation
        # self.gender = gender
        # self.solo_group = solo_group
        self.genre = genre

        self._awards = None
        self._intro = None

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

        awards_dd = soup.select('div.section_atistinfo01 dd')
        if awards_dd:
            awards_list = [item.get_text(strip=True) for item in awards_dd]
        else:
            awards_list = []

        div_intro = soup.select_one('div.section_atistinfo02 div.atist_insdc')
        if div_intro:
            intro_list = []
            for item in div_intro:
                if item.name == 'br':
                    intro_list.append('\n')
                elif type(item) is NavigableString:
                    intro_list.append(item.strip())
            intro = ''.join(intro_list)
        else:
            intro = ''

        self._awards = awards_list
        self._intro = intro

    @property
    def awards(self):
        if not self._awards:
            self.get_detail()
        return self._awards

    @property
    def intro(self):
        if not self._intro:
            self.get_detail()
        return self._intro

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