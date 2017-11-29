# 利用requests+正则 抓取猫眼电影top100榜单
import json
import re
from multiprocessing import Pool #引入进程池实现秒抓
import requests
from requests.exceptions import RequestException


# 请求第一页
def get_one_page(url):
    try:
        headers = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36', 'Referer':'https://maoyan.com/board/4?offset=10'}
        response = requests.get(url,headers=headers)
        if response.status_code  == 200:
            print(response.status_code)
            return response.text
        return None
    except Exception:
        return None

# 对页面进行解析
def parse_one_page(html):
    pattern = re.compile('<dd>.*?board-index.*?>(\d+)</i>.*?data-src="(.*?)".*?name">'
                         '<a.*?>(.*?)</a>.*?star">(.*?)</p>.*?releasetime">(.*?)</p>'
                         '.*?integer">(.*?)</i>.*?fraction">(.*?)</i>.*?</dd>', re.S)
    items = re.findall(pattern, html)
    for item in items:
        yield {
            'index': item[0],
            'image': item[1],
            'title': item[2],
            'actor': item[3].strip()[3:],
            'time': item[4].strip()[5:],
            'score': item[5] + item[6]
        }
# 存储到文件中去
def write_to_file(content):
    with open('result.txt', 'a', encoding='utf-8') as f:
        f.write(json.dumps(content,ensure_ascii=False) + '\n')
        f.close()
def main(offset):
    url = "https://maoyan.com/board/4?offset=" + str(offset)
    html = get_one_page(url)
    for item in parse_one_page(html):
        print(item)
        write_to_file(item)
if __name__ == '__main__':
    #0-90循环页面输出
    for i in range(10):
        main(i * 10)

    # pool = Pool()
    # pool.map(main, [i * 10 for i in range(10)])

