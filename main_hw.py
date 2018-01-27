from utils_r.models_hw import MelonCrawler

if __name__ == '__main__':
    crawler = MelonCrawler()
    q1 = input("검색할 곡명을 입력해주세요: ")
    search_song_list = crawler.search_song(q1)
    for item in search_song_list:
        print(item)
    q2 = input("검색할 아티스트를 입력해주세요: ")
    search_artist_list = crawler.search_artist(q2)
    for item in search_artist_list:
        print(item)
        print(item.get_songs(refresh_html=True))
        print('\n')