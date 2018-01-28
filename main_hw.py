from utils_r.models_hw import MelonCrawler

if __name__ == '__main__':
    crawler = MelonCrawler()

    # q1 = input("검색할 곡명을 입력해주세요: ")
    # search_song_list = crawler.search_song(q1)
    # for item in search_song_list:
    #     print(item)
    # q2 = input("검색할 아티스트를 입력해주세요: ")
    # search_artist_list = crawler.search_artist(q2)
    # for item in search_artist_list:
    #     print(item)
    #     print(item.get_songs(refresh_html=True))
    #     print(item.award_history)
    #     print(item.introduction)
    #     print('\n')

    artists = crawler.search_artist('아이유')
    iu = artists[0]
    print('iu.info')
    print(iu.info)
    print('')

    print('iu.award_history')
    print(iu.award_history)
    print('')

    print('iu.introduction')
    print(iu.introduction)
    print('')

    print('iu.activity_information')
    print(iu.activity_information)
    print('')

    print('iu.personal_information')
    print(iu.personal_information)
    print('')

    print('iu.related_information')
    print(iu.related_information)
    print('')

    artists = crawler.search_artist('아이유악대')
    dutbozap = artists[0]
    print('dutbozap.info')
    print(dutbozap.info)
    print('')

    print('dutbozap.award_history')
    print(dutbozap.award_history)
    print('')

    print('dutbozap.introduction')
    print(dutbozap.introduction)
    print('')

    print('dutbozap.activity_information')
    print(dutbozap.activity_information)
    print('')

    print('dutbozap.personal_information')
    print(dutbozap.personal_information)
    print('')

    print('dutbozap.related_information')
    print(dutbozap.related_information)
    print('')