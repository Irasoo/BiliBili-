from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time

# 设置Chrome浏览器驱动路径
driver_path = "E:/chromedriver/chromedriver.exe"
service = Service(driver_path)

# 启动Chrome浏览器
driver = webdriver.Chrome(service=service)

# 访问目标网址
url = "https://www.bilibili.com/v/popular/weekly?num=292"
driver.get(url)

# 等待页面加载完成（可根据情况增加等待时间）
time.sleep(5)

# 获取渲染后的HTML内容
html_content = driver.page_source

# 保存内容到文件
with open("rendered_page_source.html", "w", encoding="utf-8") as file:
    file.write(html_content)

print("渲染后的HTML源码已保存到 'rendered_page_source.html' 文件中")

# 关闭浏览器
driver.quit()

from bs4 import BeautifulSoup
import re

# 读取保存的HTML文件
with open("rendered_page_source.html", "r", encoding="utf-8") as file:
    html_content = file.read()

# 使用BeautifulSoup解析HTML
soup = BeautifulSoup(html_content, "html.parser")

# 查找所有的视频卡片
# 可能有很多链接，但是在这个页面的html中，每个video-card中只有一个链接，且就是视频的播放链接
video_cards = soup.find_all("div", class_="video-card")

# 遍历每个视频卡片并提取数据
for card in video_cards:
    # 提取视频标题
    title_element = card.find("p", class_="video-name")
    title = title_element.get_text(strip=True) if title_element else "无标题"

    # 提取UP主名称
    up_name_element = card.find("span", class_="up-name__text")
    up_name = up_name_element.get_text(strip=True) if up_name_element else "无UP主"

    # 提取播放量
    play_element = card.find("span", class_="play-text")
    play_count = play_element.get_text(strip=True) if play_element else "无播放量"

    # 提取弹幕数
    danmu_element = card.find("span", class_="like-text")
    danmu_count = danmu_element.get_text(strip=True) if danmu_element else "无弹幕数"

    # 提取标签
    tag_element = card.find("span", class_="weekly-hint")
    tag = tag_element.get_text(strip=True) if tag_element else "无标签"

    # 提取视频播放链接
    link_element = card.find("a", href=True)
    video_link = "https:" + link_element["href"] if link_element else "无链接"

    # 打印提取的数据
    print(f"标题: {title}")
    print(f"UP主: {up_name}")
    print(f"播放量: {play_count}")
    print(f"弹幕数: {danmu_count}")
    print(f"标签: {tag}")
    print(f"播放链接: {video_link}")
    print("-" * 40)

print("数据提取完成")