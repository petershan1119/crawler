import re
from bs4 import BeautifulSoup
from utils import *


if __name__ == '__main__':
    result = get_top100_list(refresh_html=True)
    for item in result:
        print(item)