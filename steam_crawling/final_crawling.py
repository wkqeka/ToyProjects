'''
# 이 부분은 처음 한번만 실행하면 됌.
# 코드 수정 - "The reason is that the last Ubuntu update update supports chromium driver just via snap."
# 최근 우분투 업데이트에서 크롬 드라이버 설치를 snap을 이용해서만 하도록 바뀜
# 고로 snap 없이 설치하는 아래 우회 코드로 변경
# 출처 : https://colab.research.google.com/drive/1cbEvuZOhkouYLda3RqiwtbM-o9hxGLyC
# 출처2 : https://stackoverflow.com/questions/75155063/selenium-use-chrome-on-colab-got-unexpectedly-exited

%%shell
# Ubuntu no longer distributes chromium-browser outside of snap
#
# Proposed solution: https://askubuntu.com/questions/1204571/how-to-install-chromium-without-snap

# Add debian buster
cat > /etc/apt/sources.list.d/debian.list <<'EOF'
deb [arch=amd64 signed-by=/usr/share/keyrings/debian-buster.gpg] http://deb.debian.org/debian buster main
deb [arch=amd64 signed-by=/usr/share/keyrings/debian-buster-updates.gpg] http://deb.debian.org/debian buster-updates main
deb [arch=amd64 signed-by=/usr/share/keyrings/debian-security-buster.gpg] http://deb.debian.org/debian-security buster/updates main
EOF

# Add keys
apt-key adv --keyserver keyserver.ubuntu.com --recv-keys DCC9EFBF77E11517
apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 648ACFD622F3D138
apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 112695A0E562B32A

apt-key export 77E11517 | gpg --dearmour -o /usr/share/keyrings/debian-buster.gpg
apt-key export 22F3D138 | gpg --dearmour -o /usr/share/keyrings/debian-buster-updates.gpg
apt-key export E562B32A | gpg --dearmour -o /usr/share/keyrings/debian-security-buster.gpg

# Prefer debian repo for chromium* packages only
# Note the double-blank lines between entries
cat > /etc/apt/preferences.d/chromium.pref << 'EOF'
Package: *
Pin: release a=eoan
Pin-Priority: 500


Package: *
Pin: origin "deb.debian.org"
Pin-Priority: 300


Package: chromium*
Pin: origin "deb.debian.org"
Pin-Priority: 700
EOF

# Install chromium and chromium-driver
apt-get update
apt-get install chromium chromium-driver

# Install selenium
pip install selenium
'''
import os
import time

# 정적 크롤링할 때 사용하는 라이브러리
import requests
from bs4 import BeautifulSoup
import urllib.request

# 동적 크롤링할 때 사용하는 라이브러리
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from tkinter import messagebox



# 태그 분류 할 때 사용되는 클래스
class Gametags:
  __user_tags = []
  
  def __init__(self, tags = ['Action', 'Arcade','RPG','Sports','Racing','Simulation','Adventure']):
    self.__user_tags = tags
  
  def compare_tags(self, tags):
    temp = []
    for index,i in enumerate(tags):
      for j in range(len(self.__user_tags)):
        if (self.__user_tags[j] == i):
          temp.append(i)
    return temp
  
def make_file():
  if(os.path.exists("./steam_data")):
     return
  else:
    files = os.mkdir("./steam_data") 
  f = open('./steam_data/data_save.txt', 'w', encoding = 'utf-8')

def scroll_down(_driver, _count):
    for _ in range(_count + 1):
       _driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
       time.sleep(1)

options = webdriver.ChromeOptions()
# options.add_argument('--headless')        # Head-less 설정
# options.add_argument('--no-sandbox')
# options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome('chromedriver', options=options)

# 파일 처리
# 파일 만들고 저장하기
make_file()
f = open('./steam_data/data_save.txt', 'w', encoding = 'utf-8')
file_write = 0

# 셀레니움으로 스팀 사이트 접속
url_selenium = "https://store.steampowered.com/search/?specials=1" 
driver.get(url_selenium)

# 스크롤을 아래로 내림
scroll_down(driver, 20)
time.sleep(5)

# 받아온 HTML 코드를 사용하여 크롤링 작업 수행
soup = BeautifulSoup(driver.page_source, 'html.parser')

# 가격 미리 처리
prices = driver.find_elements(By.CSS_SELECTOR,".search_price.discounted")
price_list = []

for element in prices:
  price = element.text.strip()
  price = price.replace('\n',' ')
  price_list.append(price)

# 게임 링크들 미리 처리
game_links = driver.find_elements(By.CLASS_NAME,'search_result_row')

# 게임에 대한 정보를 가져오기
if driver.page_source != None:
    # 반복문으로 평점 여러개 추출 가능
    for game_link, (price_index, game) in zip(game_links, enumerate(soup.find_all("a", {"class": "search_result_row"}))):
    # 게임 제목
        title = game.find("span", {"class": "title"}).text
    
    # 게임 출시 날짜
        release_date = game.find("div", {"class": "search_released"}).text.strip()

    # 게임 가격 (달러로 출력됨) 
        game_price = game.find("div", {"class": "col search_price discounted responsive_secondrow"})
        if game_price is None:
            print(price_index)
            continue
        discounted_price_element = game_price.select_one('div.search_price.discounted.responsive_secondrow > span')
        discounted_price = discounted_price_element.text.strip() if discounted_price_element else None

    # 게임 평점
        rating_response = game.select_one('div.search_reviewscore > span')
        if rating_response is not None:
            rating = rating_response.get('data-tooltip-html').split('<br>')[0]  # 평점의 정도
        rating_count = rating_response.get('data-tooltip-html').split('<br>')[1] if rating_response else None # 리뷰 수

    # 게임 태그
        url_game = game_link.get_attribute('href')
        game_res = requests.get(url_game)
        game_soup = BeautifulSoup(game_res.text,'html.parser')
        game_tags = [i.text.strip() for i in game_soup.select('#glanceCtnResponsiveRight .glance_tags.popular_tags > a')]
        default_tags = Gametags()
        result_tags = ['etc']
        result_tags = default_tags.compare_tags(game_tags)
        if not result_tags:
            result_tags = ['etc']
    
    # 파일에 분류해서 저장
        if result_tags[0] == 'Sports' or result_tags[0] == 'Racing':
            file_write = open('./steam_data/Sports_and_Racing.txt', "a", encoding='UTF8')
        else:
            file_write = open(f'./steam_data/{result_tags[0]}.txt', "a", encoding='UTF8')

        if price_index >= len(price_list):
           messagebox.showwarning("스팀게임찾기", "게임의 크롤링이 완료되었습니다.")
           break

        file_write.write(f"{title}*{release_date}*{rating}*{rating_count}*{price_list[price_index]}*{result_tags[0]}\n") 
        f.write(f"{title}*{release_date}*{rating}*{rating_count}*{price_list[price_index]}*{result_tags[0]}\n")
else : 
    print("페이지를 불러오는 데 실패했습니다")


f.close()
file_write.close()

# 셀레니움 종료
driver.quit()

# # 파일에 있는 값 불러와서 출력하기
# f = open('/content/drive/MyDrive/data_save.txt','r')

# while(True):
#   temp_string = f.readline()
#   if not temp_string:
#         break
#   print(temp_string, end = "")

# f.close()