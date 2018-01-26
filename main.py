from utils import get_top100_list, get_song_detail

if __name__ == '__main__':
    result = get_top100_list()
    # for item in result:
    #     print(f'{item["rank"]:3}: {item["title"]}')
    song_detail = []
    for i, item in enumerate(result):
        # song_detail.append(item['song_id'])
        song_detail.append(get_song_detail(item['song_id']))
        print("Being iterated!{}".format(i))
    print(song_detail)
    print("Finished")