import feedparser
import pprint
import requests
from bs4 import BeautifulSoup
import re
import NotionApi
import time


def film_info1(item):
    # 参数说明：电影名称title 封面链接cover_url 观影时间watch_time 电影链接movie_url 评分score

    # title = item["title"].split("看过")[1]
    # print(title)

    # 海报链接
    pattern = re.compile(r'(?<=src=").+(?=")', re.I)
    cover_url = re.findall(pattern, item["summary"])[0]
    cover_url = cover_url.replace("s_ratio_poster", "r")
    # print(cover_url)
    # print(item)

    # 观看时间
    time = item["published"]
    pattern2 = re.compile(r'(?<=. ).+\d{4}', re.S)  # 匹配时间
    month_satandard = {'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'May': '05', 'Jun': '06',
                       'Jul': '07', 'Aug': '08', 'Sep': '09', 'Oct': 10, 'Nov': '11', 'Dec': '12'}
    time = re.findall(pattern2, time)[0]
    time = time.split(" ")
    day = time[0]
    month = month_satandard[time[1]]
    year = time[2]
    watch_time = year + "-" + month + "-" + day
    # print(watch_time)

    # 电影链接
    movie_url = item["link"]
    # print(movie_url)

    # 处理评分
    score=item["summary"]
    pattern = re.compile(r'(?<=推荐: ).+(?=</p>)', re.S)  # 匹配评分
    # 一星：很差 二星：较差 三星：还行 四星：推荐 五星：力荐
    scoredict = {'很差': '★☆☆☆☆', '较差': '★★☆☆☆', '还行': '★★★☆☆', '推荐': '★★★★☆', '力荐': '★★★★★', }
    score = re.findall(pattern, score)
    score = scoredict[score[0]]

    return cover_url, watch_time, movie_url, score


def film_info2(movie_url):
    # 目前想改进的有title，类型，导演

    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53'}
    output = {}
    url = movie_url
    res = requests.get(url, headers=headers)
    bstitle = BeautifulSoup(res.text, 'html.parser')
    moive_content = bstitle.find_all('div', id='content')[0]

    # 电影名称与年份
    title = moive_content.find('h1')
    title = title.find_all('span')
    title = title[0].text + title[1].text
    # print(title)

    # 基本信息
    base_information = moive_content.find('div', class_='subject clearfix')
    info = base_information.find('div', id='info').text.split('\n')
    info = ','.join(info)
    # print(info)

    pattern_type = re.compile(r'(?<=类型: )[\u4e00-\u9fa5 /]+', re.S)
    movie_type = re.findall(pattern_type, info)[0].replace(" ", "").split("/")
    print(movie_type)
    # “\u4e00”和“\u9fa5”是unicode编码，并且正好是中文编码的开始和结束的两个值，所以这个正则表达式可以用来判断字符串中是否包含中文。
    pattern_director = re.compile(r'(?<=导演: )[\u4e00-\u9fa5^a-z^A-Z]+', re.I)
    # \u4e00-\u9fa5^a-z^A-Z^0-9

    director = re.findall(pattern_director, info)[0].replace(" ", "").split("/")
    print(director)

    '''
    replace（）是替换函数
    操作：a.replace('\n','')   #把a中的换行符删掉
    两个参数，第一个参数是被替换内容，第二个参数是替换内容。即第二个替换第一个。
    '''
    return title, movie_type, director

# 主程序
if __name__ == '__main__':

    # 开始连接notion

    # 改进：加入重试机制，加入防止重复
    # notion相关配置
    # 需要在notionAPI.py中配置notion token
    # 在notion Windows app的我的workspace的database的share的copylink↓
    # https://www.notion.so/5514b24ef9c84ddb89dc6ee707e9d2d0?v=e12f8f2a6c004ea8a3adbe8a9e8bfc32中间
    # 那一串是databaseid
    database_id = "5514b24ef9c84ddb89dc6ee707e9d2d0"
    rss_movie_tracker = feedparser.parse("https://www.douban.com/feed/people/erisio/interests")
    # pprint.pprint(rss_movietracker)
    # item = rss_movietracker["entries"][1]
    # print(item)
    notion_moives = NotionApi.database_item_query(database_id)
    # print(notion_moives)

for item in rss_movie_tracker["entries"]:
    if "看过" not in item["title"]:
        continue
    coverURL, watchTime, movieURL, score = film_info1(item)
    rel = NotionApi.select_items_form_databaseitems(notion_moives, "影片链接", movieURL)
    if rel:
        continue
    title, movie_type, director = film_info2(movieURL)

    body = {
        'properties': {
            '名称': {
                'title': [{'type': 'text', 'text': {'content': str(title)}}]
            },
            '观看时间': {'date': {'start': str(watchTime)}},
            '评分': {'type': 'select', 'select': {'name': str(score)}},
            '封面': {
                'files': [{'type': 'external', 'name': '封面', 'external': {'url': str(coverURL)}}]
            },
            '影片链接': {'type': 'url', 'url': str(movieURL)},
            '类型': {'type': 'multi_select', 'multi_select': [{'name': str(itemm)} for itemm in movie_type]},
            '导演': {'type': 'multi_select', 'multi_select': [{'name': str(itemm)} for itemm in director]},
        }
    }
    print(body)
    NotionApi.database_additem(database_id, body, title)
    time.sleep(3)