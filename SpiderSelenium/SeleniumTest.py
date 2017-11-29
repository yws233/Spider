import re

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pyquery import PyQuery as pq
from config import *
import pymongo
client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]

browser = webdriver.Firefox()
wait = WebDriverWait(browser, 10)
def serach():
    try:
        browser.get('https://www.taobao.com')
        element = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#q"))
        )
        submit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'.btn-search')))
        element.send_keys('美食')
        submit.click()
        #控制翻页
        total = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'.total'))) #总页数
        get_products()
        return total.text
    except TimeoutError:
        return serach()
def next_page(page_number):
    try:
        element = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input.input:nth-child(2)"))
        )
        submit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'span.btn:nth-child(4)')))
        element.clear()
        element.send_keys(page_number)
        submit.click()
        wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR,'span.num'),str(page_number)))
        get_products()
    except TimeoutException:
        next_page(page_number)
# 获取宝贝信息
def get_products():
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#mainsrp-itemlist .items .item')))
    html = browser.page_source
    doc = pq(html)
    items = doc("#mainsrp-itemlist .items .item").items()
    for item in items:
        product = {
            'image': item.find('.pic .img').attr('src'),
            'price': item.find('.price').text(),
            'deal': item.find('.deal-cnt').text()[:-3],#从最前面到倒数第三个
            'title': item.find('.title').text(),
            'shop': item.find('.shop').text(),
            'location': item.find('.location').text()

        }
        print(product)
        save_to_mongo(product)
def save_to_mongo(result):
    try:
        if db[MONGO_TABLE].insert(result):
            print("储存到mongodb数据库成功！！！！",result)
    except Exception:
        print("储存到mongodb数据库失败！！！！", result)
def main():
    total = serach()
    total = int(re.compile('(\d+)').search(total).group(1))
    #循环翻页
    for i in range(2,total+1):
        next_page(i)
        i = i + 1
        print("》》》》》》》》》》》》目前在第"+i+"页！！！！！！！")
if __name__ == '__main__':
    main()

