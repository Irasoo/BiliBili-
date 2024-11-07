from crawler.chrome_web_driver import ChromeWebDriver
from commom.env_tools import get_env_var
from bs4 import BeautifulSoup
from typing import List, Dict
from commom.schemas import VideoDetailedInfo
from concurrent.futures import  ThreadPoolExecutor, as_completed

import pandas as pd
import os
import datetime


class BilibiliCrawler:
     __slots__ = (
         "chrome_driver",
         "bilibili_data",
         "max_workers"
     )

     def __init__(self, sleep_time: int=5, max_workers: int=5):
         self.chrome_driver = ChromeWebDriver(driver_path=get_env_var(var_name="DRIVER_PATH"), sleep_time=sleep_time)
         self.bilibili_data: List[VideoDetailedInfo] = []
         self.max_workers = max_workers

     def get_weekly_popular_video_list_info(self, url: str):
         if "https://www.bilibili.com/v/popular/weekly" not in url:
             raise ValueError(f"Please enter the relevant URL, which must include the 'https://www.bilibili.com/v/popular/weekly' fields")

         weekly_list_html_content = self.chrome_driver.get_html_content(target_url=url)
         soup = BeautifulSoup(weekly_list_html_content, "html.parser")

         # 查找所有的视频卡片
         # 可能有很多链接，但是在这个页面的html中，每个video-card中只有一个链接，且就是视频的播放链接
         video_cards = soup.find_all("div", class_="video-card")

         video_info_list = []

         # 遍历每个视频卡片并提取数据
         for card in video_cards:
             # 提取视频标题
             title_element = card.find("p", class_="video-name")
             title = title_element.get_text(strip=True) if title_element else "missing value"

             # 提取UP主名称
             up_name_element = card.find("span", class_="up-name__text")
             up_name = up_name_element.get_text(strip=True) if up_name_element else "missing value"

             # 提取播放数量
             play_element = card.find("span", class_="play-text")
             play_count = play_element.get_text(strip=True) if play_element else "无播放量"

             # 提取视频播放链接
             link_element = card.find("a", href=True)
             video_link = "https:" + link_element["href"] if link_element else "missing value"

             # 提取弹幕数
             danmu_element = card.find("span", class_="like-text")
             danmu_count = danmu_element.get_text(strip=True) if danmu_element else "missing value"

             video_info = {}
             video_info["title"] = title
             video_info["up_name"] = up_name
             video_info["video_link"] = video_link
             video_info['danmu_count'] = danmu_count
             video_info['play_count'] = play_count

             video_info_list.append(video_info)

         return video_info_list

     def get_single_video_info(self, url: str) -> Dict[str, str | list]:
         if "https://www.bilibili.com/video/" not in url:
             raise ValueError("Please enter a URL containing 'https://www.bilibili.com/video/'")

         video_info = {}

         # 先获取普通HTML内容
         html_content = self.chrome_driver.get_html_content(target_url=url)
         soup = BeautifulSoup(html_content, "html.parser")

         # 获取页面上的非shadow-root内容
         # 获取点赞数量
         like_count_element = soup.find("span", class_="video-like-info video-toolbar-item-text")
         like_count = like_count_element.get_text(strip=True) if like_count_element else "missing value"

         # 获取投币数量
         coin_count_element = soup.find("span", class_="video-coin-info video-toolbar-item-text")
         coin_count = coin_count_element.get_text(strip=True) if coin_count_element else "missing value"

         # 获取收藏数量
         fav_count_element = soup.find("span", class_="video-fav-info video-toolbar-item-text")
         fav_count = fav_count_element.get_text(strip=True) if fav_count_element else "missing value"

         # 获取转发数量
         share_count_element = soup.find("span", class_="video-share-info-text")
         share_count = share_count_element.get_text(strip=True) if share_count_element else "missing value"

         # 获取标签列表
         tags_element = soup.find_all("a", class_="tag-link")
         tag_list = [tag.get_text(strip=True) for tag in tags_element if tag]

         # 获取粉丝数量
         # 前提是不能关注此UP，否则存储了粉丝数的html元素的class会发生改变
         fans_count_element = soup.find("span", class_="follow-btn-inner")
         fans_count = fans_count_element.get_text(strip=True) if fans_count_element else "missing value"

         # 获取shadow-root中的内容
         # 获取评论数
         comment_count = self.chrome_driver.get_shadow_root_content(target_url=url, selectors=["bili-comments", "bili-comments-header-renderer", "#count"])

         # 信息汇总
         video_info["like_count"] = like_count
         video_info["coin_count"] = coin_count
         video_info["fav_count"] = fav_count
         video_info["share_count"] = share_count
         video_info["fans_count"] = fans_count
         video_info["tags"] = tag_list if tag_list else "missing value"
         video_info["comment_count"] = comment_count if comment_count else "missing value"

         return video_info

     def get_weekly_popular_video_detailed_info(self, url: str):
         # 先获取每周必看视频的基本信息
         video_info_weekly_list = self.get_weekly_popular_video_list_info(url)

         # 定义线程池并发数
         max_workers = self.max_workers

         # 定义任务函数，用于线程池中调用
         def fetch_single_video_info(video_info_in_list):
             single_video_url = video_info_in_list["video_link"]
             single_video_info = self.get_single_video_info(single_video_url)
             video_info_combined = {
                 "title": video_info_in_list["title"],
                 "video_link": video_info_in_list["video_link"],
                 "up_name": video_info_in_list["up_name"],
                 "play_count": video_info_in_list["play_count"],
                 "danmu_count": video_info_in_list["danmu_count"],
                 "like_count": single_video_info["like_count"],
                 "coin_count": single_video_info["coin_count"],
                 "fav_count": single_video_info["fav_count"],
                 "share_count": single_video_info["share_count"],
                 "comment_count": single_video_info["comment_count"],
                 "fans_count": single_video_info["fans_count"],
                 "tags": single_video_info["tags"],
             }
             return video_info_combined

         # 使用线程池执行任务
         with ThreadPoolExecutor(max_workers=max_workers) as executor:
             # 将每个视频的爬取任务提交到线程池
             future_to_video = {executor.submit(fetch_single_video_info, video): video for video in
                                video_info_weekly_list}
             for future in as_completed(future_to_video):
                 video_info_combined = future.result()
                 self.bilibili_data.append(video_info_combined)
                 print("Title:", video_info_combined["title"])
                 print("Video Link:", video_info_combined["video_link"])
                 print("Up Name:", video_info_combined["up_name"])
                 print("Fans Count", video_info_combined["fans_count"])
                 print("Play Count:", video_info_combined["play_count"])
                 print("Danmu Count:", video_info_combined["danmu_count"])
                 print("Like Count:", video_info_combined["like_count"])
                 print("Coin Count:", video_info_combined["coin_count"])
                 print("Fav Count:", video_info_combined["fav_count"])
                 print("Share Count:", video_info_combined["share_count"])
                 print("Comment Count:", video_info_combined["comment_count"])
                 print("Tags:", video_info_combined["tags"])
                 print("-" * 40)



     def bilibili_data_to_csv(self, save_name: str, save_path: str = "data/raw_data"):
         # 如果保存路径不存在，则创建它
         os.makedirs(save_path, exist_ok=True)

         # 生成完整文件路径，文件名包括时间戳
         file_name = f"{save_name}.csv"
         file_path = os.path.join(save_path, file_name)

         # 将数据保存到 CSV 文件中
         try:
             df = pd.DataFrame(self.bilibili_data)
             df.to_csv(file_path, index=False, encoding="utf-8-sig")
             print(f"Data saved to {file_path}")
         except Exception as e:
             print(f"Failed to save data to CSV: {e}")


if __name__ == '__main__':
    crawler = BilibiliCrawler(sleep_time=5)

    weekly_url = "https://www.bilibili.com/v/popular/weekly?num=292"  # 替换为实际链接
    crawler.get_weekly_popular_video_detailed_info(url=weekly_url)

    save_name = "test-292"
    csv_path = crawler.bilibili_data_to_csv(save_name=save_name)

    print("CSV 文件已保存到:", csv_path)




