from dis import code_info

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup
import re

# 设置Chrome浏览器驱动路径
driver_path = "E:/chromedriver/chromedriver.exe"
service = Service(driver_path)

# 启动Chrome浏览器
driver = webdriver.Chrome(service=service)

# 访问目标网址
url = "https://www.bilibili.com/video/BV1tUycYNEo5"
driver.get(url)

# 等待页面加载完成（可根据情况增加等待时间）
time.sleep(10)

# 获取渲染后的HTML内容
html_content = driver.page_source

# 退出浏览器
driver.quit()

# 使用BeautifulSoup解析HTML
soup = BeautifulSoup(html_content, "html.parser")

# 查找所有的视频卡片
# 可能有很多链接，但是在这个页面的html中，每个video-card中只有一个链接，且就是视频的播放链接

like_count_element = soup.find("span", class_="video-like-info video-toolbar-item-text")
like_count = like_count_element.get_text(strip=True) if like_count_element else "无播放量"

coin_count_element = soup.find("span", class_="video-coin-info video-toolbar-item-text")
coin_count = coin_count_element.get_text(strip=True) if coin_count_element else "无硬币数"

fav_count_element = soup.find("span", class_="video-fav-info video-toolbar-item-text")
fav_count = fav_count_element.get_text(strip=True) if fav_count_element else "无收藏数"

share_count_element = soup.find("span", class_="video-share-info-text")
share_count = share_count_element.get_text(strip=True) if share_count_element else "无转发数"

comment_count_element = soup.find("div", id="navbar")
print(comment_count_element)
comment_count = comment_count_element.get_text(strip=True) if comment_count_element else "无评论数"


print(like_count, coin_count, fav_count, share_count, comment_count)

tags_element = soup.find_all("a", class_="tag-link")
tag_list = []
for tag_element in tags_element:
    tag_list.append(tag_element.get_text(strip=True) if tag_element else "无效tag")

print(tag_list)
