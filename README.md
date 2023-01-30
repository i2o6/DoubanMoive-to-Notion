
---

# 前言
本文基于2022-05-28，之后可能会发生一些api之类的改变
---

**参考文章**
[利用Python爬虫+notion API实现在notion中自动收录看过的电影](https://zhuanlan.zhihu.com/p/425067213)
[notion API命令-个性化再封装](https://zhuanlan.zhihu.com/p/395219868)
[如何使用python+notion API搭建属于自己的豆瓣观影记录](https://zhuanlan.zhihu.com/p/521182229)

**个人思路**
通过python将`豆瓣个人页面的观影记录`到`notion`的观影记录页面中，如果再搭配上windows的类似于定时任务的功能，每隔一段时间自动运行一次，就可以实现自动化的豆瓣填写影评，更新到notion中。

注意：个人主页只显示最近看过的五部电影

此功能不光可以将豆瓣个人观影记录导入到notion，只要可以通过python导入的都可以，包括博客之类的
**需要提前准备的东西：**
1. 有在豆瓣记录观影记录的习惯
2. notion相对应的电影模板页，[我分享一个自己的在这里](https://best-tank-15d.notion.site/Movie-Tracker-1b086df62e3b4c0fb9a669daff64ba3f)
3. 电脑上有python,需要安装`feedparser`,`pprint`,`BeautifulSoup`,`re`这些包
4. 所有代码已经上传到我的[Github仓库](https://github.com/moji111/doubanMoive2Notion)
5. notion API官网在这里 [Notion API](https://developers.notion.com/)

---

# 一、得到豆瓣观影数据
在个人主页https://www.douban.com/people/你的豆瓣id/ 
`你的豆瓣id需要进行替换` 页面右下方会有rss订阅，这个数据是跟着你的信息同步更新的，只要有这个链接就可以获得你最近看过的电影，想看的电影，看的书等等信息。
![在这里插入图片描述](https://img-blog.csdnimg.cn/12577dc59f3d4c8792ee03f0c2fb69c9.png#pic_center)
经过百度之后，我使用的`pprint`和`feedparser`来处理rss链接信息
```python
import feedparser
import pprint
rss_movietracker = feedparser.parse("https://www.douban.com/feed/people/148064238/interests")
pprint.pprint(rss_movietracker)
```
可以看一下大概的输出，是一个类似于json的文件，其中我们需要的电影的信息都在`entries`里面
![在这里插入图片描述](https://img-blog.csdnimg.cn/464190ec1d814855a118fac8d809af44.png#pic_center)
# 二、处理豆瓣得到的数据
rss中取得的信息是这样的：如果我们把`rss_movietracker["entries"]`看作一个list，那么这个list当中的每一个item都是我们个人主页（只显示最近看过的）的一个物品，比如看过的每一部电影，想看的每一部电影，看过的每一本图书，所以我们只需要对每个item进行处理，得到我们想要的信息即可。
![在这里插入图片描述](https://img-blog.csdnimg.cn/68e333df50634f319c89391134182239.png#pic_center)
<center>我的notion观影模板需要的信息</center>

接下来是对每一个item进行处理，`title`, `cover_url`, `score`, `watch_time`, `comment`, `movie_url`都可以在item中拿到，所以我定义了一个函数来得到这些。
```python
def film_info1(item):
# 名称title 封面链接cover_url 观影时间watch_time 电影链接movive_url 评分score 评论 comment
    pattern1 = re.compile(r'(?<=src=").+(?=")', re.I)  # 匹配海报链接
    title = item["title"].split("看过")[1]
# print(title)
    cover_url = re.findall(pattern1, item["summary"])[0]
    cover_url = cover_url.replace("s_ratio_poster", "r")
# print(cover_url)
    time = item["published"]
    pattern2 = re.compile(r'(?<=. ).+\d{4}', re.S)  # 匹配时间
    month_satandard = {'January': '01', 'February': '02', 'March': '03', 'April': '04', 'May': '05', 'June': '06',
                   'July': '07', 'August': '08', 'September': '09', 'October': 10, 'November': '11', 'December': '12'}
    time = re.findall(pattern2, time)[0]
    time = time.split(" ")
    day = time[0]
    month = month_satandard[time[1]]
    year = time[2]
    watch_time = year + "-" + month + "-" + day
# print(watch_time)

    movie_url = item["link"]


# 处理comment
# print(item["summary"])
    pattern = re.compile(r'(?<=<p>).+(?=</p>)', re.S)  # 匹配评论·
# pattern2 = re.compile(r'(?<=<p>)(.|\n)+(?=</p>)', re.I) # 匹配评论·
    allcomment = re.findall(pattern, item["summary"])[0]  # 需要进一步处理
# print(allcomment)
    pattern1 = re.compile(r'(?<=推荐: ).+(?=</p>)', re.S)  # 匹配评分
# 一星：很差 二星：较差 三星：还行 四星：推荐 五星：力荐
    scoredict = {'很差': '⭐', '较差': '⭐⭐', '还行': '⭐⭐⭐', '推荐': '⭐⭐⭐⭐', '力荐': '⭐⭐⭐⭐⭐', }
    score = re.findall(pattern1, allcomment)
    if score:
        score = scoredict[score[0]]
    else:
        score = "⭐⭐⭐"
# print(score)

    pattern2 = re.compile(r'(?<=<p>).+', re.S)  # 匹配评价
    comment = re.findall(pattern2, allcomment)[0]
    comment = comment.split("备注: ")[1]

    return title, cover_url, watch_time, movie_url, score, comment
```
接下来需要得到movie_type和director两个属性，这两个属性只能从电影的详情页面得到。同时目前的title只有中文，想改进成中文＋原国家语言 + 年份的形式。
ps.这一段代码主要来自知乎用户@无尾羊
```python
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

    # 基本信息
    base_information = moive_content.find('div', class_='subject clearfix')
    info = base_information.find('div', id='info').text.split('\n')
    Info = {}
    for i in info:
        if len(i) > 1:
            iifo = i.split(':')
            Info[iifo[0]] = iifo[1]
    # print(info)
    info = ','.join(info)
    pattern_type = re.compile(r'(?<=类型: )[\u4e00-\u9fa5 /]+', re.S)
    movie_type = re.findall(pattern_type, info)[0].replace(" ", "").split("/")
    # print(movie_type)
    pattern_director = re.compile(r'(?<=导演: )[\u4e00-\u9fa5 /]+', re.I)
    director = re.findall(pattern_director, info)[0].replace(" ", "").split("/")
    # print(director)
    return title, movie_type, director

```
# 三、构建json数据并调用notion API

这里其实就是代码的主函数部分，这里不光有构建json数据并调用notion API，同时还有如果在rss数据中只处理看过的电影数据，notion的database中已经存在该电影的时候的处理。
```python
# 改进：加入重试机制，加入防止重复
if __name__ == '__main__':

    # notion相关配置
    databaseid = "你自己的databaseid"
    rss_movietracker = feedparser.parse("你的rss订阅链接")
    # pprint.pprint(rss_movietracker)
    #item = rss_movietracker["entries"][1]

    for item in rss_movietracker["entries"]:
        if "看过" not in item["title"]:
            break
        cover_url, watch_time, movie_url, score, comment = film_info1(item)
        rel = notionApi.select_items_form_Databaseid(databaseid, "url", movie_url)
        if rel is not None:
            continue
        title, movie_type, director = film_info2(movie_url)


        body = {
            'properties': {
                '名称': {
                    'title': [{'type': 'text', 'text': {'content': str(title)}}]
                },
                '观看时间': {'date': {'start': str(watch_time)}},
                '评分': {'type': 'select', 'select': {'name': str(score)}},
                '封面': {
                    'files': [{'type': 'external', 'name': '封面', 'external': {'url': str(cover_url)}}]
                },
                '有啥想说的不': {'type': 'rich_text',
                           'rich_text': [{'type': 'text', 'text': {'content': str(comment)}, 'plain_text': str(comment)}]},
                '影片链接': {'type': 'url', 'url': str(movie_url)},
                '类型': {'type': 'multi_select', 'multi_select': [{'name': str(itemm)} for itemm in movie_type]},
                '导演': {'type': 'multi_select', 'multi_select': [{'name': str(itemm)} for itemm in director]},

            }
        }
        print(body)
        notionApi.DataBase_additem(databaseid, body, title)

```


---

# 总结
目前代码肯定还是有一些细小的问题，希望如果有大佬看到了可以提出。
同时目前功能上有一些不够完善，没有异常的处理，甚至对于某些电影数据处理可能不够完善。
只能添加`最近看过的`几部电影，如果是想从头导入所有看过的电影的话，我这个代码是不适用的。
