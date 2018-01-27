from utils.models import MelonCrawler

if __name__ == '__main__':
    crawler = MelonCrawler()
    q = input('검색할 곡 명을 입력해주세요: ')
    search_song_list = crawler.search_song(q)