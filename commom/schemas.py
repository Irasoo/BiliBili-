from typing import List, TypedDict

# 每个“每周必看视频”的被存储的信息
class VideoDetailedInfo(TypedDict):
    title: str
    up_name: str
    fans_count: str
    danmu_count: str
    like_count: str
    coin_count: str
    fav_count: str
    share_count: str
    comment_count: str
    tags: List[str]
    relative_week_count: int  # 这个相对周计数的意思是：在按周连续的视频摘取过程中，此视频的相对周数。比如摘取从2024年第12周到15周的视频，那么爬取的第12周数据在这一连串的爬取过程就是第一周。


# UP主个人信息
class UPInfo(TypedDict):
    name: str
    frequent_tags: List[str] # UP主常用的视频标签

