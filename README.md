# 一、前言


1. 原材料：豆瓣、Notion、Python；
2. 通过豆瓣个人主页的RSS链接中获得豆瓣账户中的动态标记信息，将其与Notion数据库的接口使用Pycharm进行连接，实现我的“看过”批量记录在Notion上的功能。

*说明：只适用于最近标记过的5部电影的记录，不适用于很久之前的备份*

*改进方案关键词：机器人、自动添加、定时*


>效果预览

![image](https://user-images.githubusercontent.com/54937829/215422244-dbca0064-73eb-4ec3-929f-852f87546865.png)
![image](https://user-images.githubusercontent.com/54937829/215422287-774d50cc-7fd5-440a-9dd9-970d2b7bf6b7.png)



# 二、主要流程 


## （一）前期准备

### 1.豆瓣观影数据

(1) 在个人主页的页面右下方会有RSS链接 

`https://www.douban.com/feed/people/你的豆瓣ID/interests`  
❗注意：你的豆瓣ID需要进行替换❗

(2) 把这个链接记录在方便下次找到的地方，比如说，在桌面新建一个txt文档，或者把它复制给你的微信文件传输助手。


### 2.Notion创建新的DataBase并获取DataBaseID

(1) 新建一个Table

![创建DataBase](https://user-images.githubusercontent.com/54937829/215414232-f8c3700e-d403-4cc3-b085-4b3fd030be15.png)

(2) 新建属性

电影名 - Title

封面 - Files & media

类型 - Multi-select

导演 - Multi-select

评分 - Select

观看时间 - Date

影片 - URL

*后续可以根据自己的偏好进行删减*

![create property](https://user-images.githubusercontent.com/54937829/215416190-56d98930-8c5a-4327-985c-4df1072600d6.png)
![preview](https://user-images.githubusercontent.com/54937829/215416636-7018cc24-05d9-4f9d-9bd6-e8299d29d5dd.png)

(3)DataBaseID

* 点击页面右上角的Share可以看见右下角的Copy link的选项

* 会得到`https://www.notion.so/1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a?v=3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c` 这样一个链接

* 其中`1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a`是我们需要的databaseid，是一串32个字符的随机字符。

    ❗注意：你的databaseid需要进行替换❗

* 同样的，像前面的RSS链接一样，记录在方便查阅的地方。

    [Notion的官方说明](https://developers.notion.com/docs/working-with-databases)
    
    [参考链接2](https://neverproductive.com/database-id-notion/#:~:text=Notion%20database%20and%20page%20IDs%20are%20the%20unique,every%20database%20has%20one%20of%20those%20unique%20identifiers.)

### 3.Notion创建新的integrations并获取Token

* 首先进入Notion API官网：[Notion API](https://developers.notion.com/)
* 右上角 ↗ View my integrations
* 选择 + New integration
* 为这个集成命名，提交Submit
* Secrets → Internal Integration Token → 复制Token

    ❗注意：`secret_xxxxxxxx` 就是你的token❗ 请记录下来


---

## （二）代码部分

### 1.main类

#### 1.1 新安装的PyCharm需要安装相应的包：feedparser、bs4、requests等

安装路径 File -> Settings -> Project:工程项目名 -> Python interpreter -> ➕


#### 1.2 导入库import

```python
from bs4 import BeautifulSoup
import NotionApi
import feedparser
import requests
import pprint
import time
import re


```

#### 1.3 处理RSS链接

```python
rss_movietracker = feedparser.parse("https://www.douban.com/feed/people/你的豆瓣ID/interests")
pprint.pprint(rss_movietracker) #使用pprint美化打印进行预览
```
输出的是一个类似于json的文件，其中我们需要的电影的信息都在`entries`里面

>输出预览

![1675130569(1)](https://user-images.githubusercontent.com/54937829/215641074-50ac80f2-6cbe-45c6-8c5f-204a50e7b9f7.png)

#### 1.4 处理豆瓣得到的数据

如果我们把`rss_movietracker["entries"]`看作一个list，那么这个list当中的每一个item都是我们个人主页（只显示最近看过的）的一个表项，比如看过的每一部电影，想看的每一部电影，看过的每一本图书，所以我们只需要对每个item进行处理，得到我们想要的信息即可。

基于先前在notion中设置的属性（电影名、封面、类型、导演、评分、观看时间、影片链接），我们将逐一从item中提取。

于是定义了一个函数`film_info1`，用来提取`title`, `cover_url`, `score`, `watch_time`,`movie_url`这五个属性。

*类型、导演后续会提到。*

```python
def film_info1(item):

    # 参数说明：电影名称title 封面链接cover_url 观影时间 watch_time 电影链接movie_url 评分score

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


```

#### 1.5 处理类型和导演属性

要得到电影类型movie_type和导演director两个属性，需要从电影的详情页面得到。


```python
def film_info2(movie_url):

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
    # \u4e00和\u9fa5是unicode编码，是中文编码的开始和结束的值，所以正则表达式\u4e00-\u9fa5 /用来判断字符串中是否包含中文。
    pattern_director = re.compile(r'(?<=导演: )[\u4e00-\u9fa5^a-z^A-Z]+', re.I)
    #考虑到电影导演若为外国人，即导演姓名由英文字母组成的情况，增加a-z^A-Z的正则式

    director = re.findall(pattern_director, info)[0].replace(" ", "").split("/")
    print(director)

    '''
    一些基础知识的复习（怕自己忘记）
    replace（）是替换函数
    操作：a.replace('\n','')   #把a中的换行符删掉
    两个参数，第一个参数是被替换内容，第二个参数是替换内容。即第二个替换第一个。
    '''
    return title, movie_type, director


```
#### 1.6 主函数：构建json数据并调用notion API

```python
    # 开始连接notion

if __name__ == '__main__':

    # notion相关配置
    database_id = "32位英文/数字字符" # 请替换为你的database_id
    rss_movie_tracker = feedparser.parse("https://www.douban.com/feed/people/你的豆瓣ID/interests") # 请替换为你的豆瓣rss链接
    # pprint.pprint(rss_movie_tracker)
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

```
### 2.Notion Api类


详见[知乎@无尾羊：notion API命令-个性化再封装](https://zhuanlan.zhihu.com/p/395219868)

```python

"""
    body = {
     'properties':{
          '我是number（这里对应你database的属性名称）':{'type': 'number', 'number': int(数据)},
          '我是title':{
                'id': 'title', 'type': 'title', 
                'title': [{'type': 'text', 'text': {'content': str(数据)}, 'plain_text': str(数据)}]
            },
          '我是select': {'type': 'select', 'select': {'name': str(数据)}},
          '我是date': {'type': 'date', 'date': {'start': str(数据), 'end': None}},
          '我是Text': {'type': 'rich_text', 'rich_text': [{'type': 'text', 'text': {'content': str(数据)},  'plain_text': str(数据)}]},
          '我是multi_select': {'type': 'multi_select', 'multi_select': [{'name': str(数据)}, {'name': str(数据)}]}
          '我是checkbox':{'type': 'checkbox', 'checkbox': bool(数据)}
     }
}
"""

import requests

# notion基本参数
token = 'secret_xxxxxxxxxxxxxxxxxxx' #请替换为你的Notion账户创建的integration的token

headers = {
    #Notion API 是版本化的. Notion API 版本以版本发布的日期命名【版本控制】
    #notion-Version header should be `"2021-05-11"`, `"2021-05-13"`, `"2021-08-16"`, `"2022-02-22"`, or `"2022-06-28"`
    'Notion-Version': '2022-06-28',
    'Connection': 'close',
    'Authorization': 'Bearer ' + token,
}


# 1. 删除页面：delete_page(page_id)
def delete_page(page_id):
    body = {
        'archived': True
    }
    url = 'https://api.notion.com/v1/pages/' + page_id
    notion = requests.patch(url, headers=headers, json=body)

    return 0


# 2. 更新页面属性：updata_page_properties(page_id,body,station)
# 其中的station用来说明你处理对象是否成功更新了属性
def updata_page_properties(page_id, body, station):
    url = 'https://api.notion.com/v1/pages/' + page_id
    notion = requests.patch(url, headers=headers, json=body)

    if notion.status_code == 200:
        print(station + '·更新成功')
    else:
        print(station + '·更新失败')

    return 0


# 3. 获取页面属性：get_page_information(page_id)
# 返回的是字典型数据，数据结构同上面的body结构相似，而内容是对应页面属性值。
def get_page_information(page_id):
    url = 'https://api.notion.com/v1/pages/' + page_id
    notion_page = requests.get(url, headers=headers)
    result = notion_page.json()
    if notion_page.status_code == 200:
        print('页面属性获取成功')
    else:
        print('页面属性获取失败')

    return result


# 4. 获取数据库中的每条数据：DataBase_item_query(query_database_id)
# 返回的是列表数据，列表数据中的每个元素是字典数据，数据结构同上面的body结构相似，
# 而内容是对应每条数据的属性值（没有数据条目限制，完全遍历你的数据库的每一条数据）。

def database_item_query(query_database_id):
    url_notion_block = 'https://api.notion.com/v1/databases/' + query_database_id + '/query'
    res_notion = requests.post(url_notion_block, headers=headers)
    S_0 = res_notion.json()
    #print(S_0)
    res_travel = S_0['results']
    if_continue = len(res_travel)
    if if_continue > 0:
        while if_continue % 100 == 0:
            body = {
                'start_cursor': res_travel[-1]['id']
            }
            res_notion_plus = requests.post(url_notion_block, headers=headers, json=body)
            S_0plus = res_notion_plus.json()

            res_travel_plus = S_0plus['results']
            for i in res_travel_plus:
                if i['id'] == res_travel[-1]['id']:
                    continue
                res_travel.append(i)
            if_continue = len(res_travel_plus)
    return res_travel


# 5. 向database数据库增加数据条目：DataBase_additem(database_id,body_properties,station)
def database_additem(database_id, body_properties, station):
    body = {
        'parent': {'type': 'database_id', 'database_id': database_id},
    }
    body.update(body_properties)

    url_notion_additem = 'https://api.notion.com/v1/pages'
    notion_additem = requests.post(url_notion_additem, headers=headers, json=body)

    if notion_additem.status_code == 200:
        print(station + '·更新成功')
    else:
        print(station + '·更新失败')


# 6.1 获取指定页面属性的指定属性值：pageid_information_pick(page_id,label)
def pageid_information_pick(page_id, label):
    x = get_page_information(page_id)

    if label == 'id':
        output = x['id']
    else:
        type_x = x['properties'][label]['type']

        if type_x == 'checkbox':
            output = x['properties'][label]['checkbox']

        if type_x == 'date':
            output = x['properties'][label]['date']['start']

        if type_x == 'select':
            output = x['properties'][label]['select']['name']

        if type_x == 'rich_text':
            output = x['properties'][label]['rich_text'][0]['plain_text']

        if type_x == 'title':
            output = x['properties'][label]['title'][0]['plain_text']

        if type_x == 'number':
            output = x['properties'][label]['number']

    return output


# 6.2 获取body结构中的指定属性值：item_information_pick(item,label)
def item_information_pick(item, label):
    x = item

    if label == 'id':
        output = x['id']
    else:
        type_x = x['properties'][label]['type']

        if type_x == 'checkbox':
            output = x['properties'][label]['checkbox']

        if type_x == 'date':
            output = x['properties'][label]['date']['start']

        if type_x == 'select':
            output = x['properties'][label]['select']['name']

        if type_x == 'rich_text':
            output = x['properties'][label]['rich_text'][0]['plain_text']

        if type_x == 'title':
            output = x['properties'][label]['title'][0]['plain_text']

        if type_x == 'number':
            output = x['properties'][label]['number']

        if type_x == 'url':
            output = x['properties'][label]['url']

    return output


# 7.1 body属性值字典数据的建立（多参数）：body_properties_input(body,label,type_x,data)
def body_properties_input(body, label, type_x, data):
    if type_x == 'checkbox':
        body['properties'].update({label: {'type': 'checkbox', 'checkbox': data}})

    if type_x == 'date':
        body['properties'].update({label: {'type': 'date', 'date': {'start': data, 'end': None}}})

    if type_x == 'select':
        body['properties'].update({label: {'type': 'select', 'select': {'name': data}}})

    if type_x == 'rich_text':
        body['properties'].update({label: {'type': 'rich_text', 'rich_text': [
            {'type': 'text', 'text': {'content': data}, 'plain_text': data}]}})

    if type_x == 'title':
        body['properties'].update({label: {'id': 'title', 'type': 'title',
                                           'title': [{'type': 'text', 'text': {'content': data}, 'plain_text': data}]}})

    if type_x == 'number':
        body['properties'].update({label: {'type': 'number', 'number': data}})

    return body


# 7.2 body属性值字典数据的建立（单参数）：body_propertie_input(label,type_x,data)
def body_propertie_input(label, type_x, data):
    body = {
        'properties': {}
    }

    if type_x == 'checkbox':
        body['properties'].update({label: {'type': 'checkbox', 'checkbox': data}})

    if type_x == 'date':
        body['properties'].update({label: {'type': 'date', 'date': {'start': data, 'end': None}}})

    if type_x == 'select':
        body['properties'].update({label: {'type': 'select', 'select': {'name': data}}})

    if type_x == 'rich_text':
        body['properties'].update({label: {'type': 'rich_text', 'rich_text': [
            {'type': 'text', 'text': {'content': data}, 'plain_text': data}]}})

    if type_x == 'title':
        body['properties'].update({label: {'id': 'title', 'type': 'title',
                                           'title': [{'type': 'text', 'text': {'content': data}, 'plain_text': data}]}})

    if type_x == 'number':
        body['properties'].update({label: {'type': 'number', 'number': data}})

    return body


# 8.1 从database数据库中筛选出符合条件的条目：select_items_form_Databaseid(Database_id,label,value)
#
# 返回值为列表型数据，该数据符合你的筛选条件的
def select_items_form_database_id(Database_id, label, value):
    items = database_item_query(Database_id)
    # print(items)
    items_pick = []

    for item in items:
        if item_information_pick(item, label) == value:
            items_pick.append(item)

    return items_pick


# 8.2 从database数据库的条目中筛选出符合条件的条目：select_items_form_Databaseitems(items,label,value)
#
# 返回值为列表型数据，该数据符合你的筛选条件的
def select_items_form_databaseitems(items, label, value):
    items_pick = []

    for item in items:
        if item_information_pick(item, label) == value:
            items_pick.append(item)

    return items_pick

```


# 三、最后

## 参考文章


[如何使用python+notion API搭建属于自己的豆瓣观影记录](https://zhuanlan.zhihu.com/p/521182229)

[notion API命令-个性化再封装](https://zhuanlan.zhihu.com/p/395219868)

[利用Python爬虫+notion API实现在notion中自动收录看过的电影](https://zhuanlan.zhihu.com/p/425067213)

1、此方案只适用于最近标记过的5部电影的记录，不适用于很久之前的备份。如果要把豆瓣里的所有标记都迁移到notion上，目前只有手动添加的办法，如果有友友知道有方法实现自动添加，烦请告诉我一下。

2、我删除了短评的代码，所以无法实现有短评的标记迁移。（因为我本人不怎么写评价，基本只评分，因而也就删去了原文的comment项

3、改进方案关键词：机器人、自动添加、定时

4、我还准备加入一个月观影的gallery view，按观影月份分类，可以看看这个月都看了哪些影视剧，进行一个月总结。


