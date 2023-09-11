import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
from datetime import datetime
import time
import os
from tqdm import tqdm
import re
import mysql.connector
import random


##오늘날짜얻기
today = datetime.today().strftime('%Y%m%d')
#print(today)

##data 폴더 생성
try:
    if not os.path.exists("data"):
        os.mkdir("data")
except OSError:
    print ('Error: Creating directory. ' +  "data")

"""
100 : 정치
101 : 경제
102 : 사회
103 : 생활/문화
104 : 세계
105 : IT/과학
"""


def cleanText(readData):
  return re.sub(" {2,}", ' ', re.sub("[\t\n\v\f\r]", '', readData))




def make_urllist(cat, date):
    global last_url
    page_num = 0
    first_url = ""
    urllist= []
    first_flag = 0
    last_flag = 0
    
    for i in range(10000):
        url = 'https://news.naver.com/main/list.nhn?mode=LSD&mid=sec&sid1='+str(cat)+'&date='+str(date)+'&page='+str(i+1)
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.90 Safari/537.36'}
        news = requests.get(url, headers=headers)

        # BeautifulSoup의 인스턴스 생성합니다. 파서는 html.parser를 사용합니다.
        soup = BeautifulSoup(news.content, 'html.parser')

        # CASE 1
        news_list = soup.select('.newsflash_body .type06_headline li dl')
        # CASE 2
        news_list.extend(soup.select('.newsflash_body .type06 li dl'))
        

        # 각 뉴스로부터 a 태그인 <a href ='주소'> 에서 '주소'만을 가져옵니다.
        for idx, line in enumerate(news_list):
            tmp_url = line.a.get('href')
            #바뀐페이지의 젓번째 url의 변동이없을때 탈출
            if idx == 0:
                if first_url == tmp_url:
                    first_flag = 1
                    break
                else:
                    first_url = tmp_url
            
            #마지막 db에 저장된 url과 비교
            if last_url[cat] == tmp_url:
                last_flag = 1
                break
            urllist.append(tmp_url)


        if first_flag == 1:
            break
        if last_flag == 1:
            break
        #뉴스 개수가 20개가 안되면 탈출
        if len(news_list) < 20:
            break

        time.sleep(random.uniform(0.8,1.5))

    return urllist
    

def send_info(cats, url_lists):
    global last_url
    # cat 값에 따라 url_list에 접근
    for cat in tqdm(cats):
        #print(f"cat {i}: {url_lists[i]}")

        #print(list(reversed(url_lists[cat])))
        for url in list(reversed(url_lists[cat])):
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"}

            res = requests.get(url, headers=headers)
            soup = BeautifulSoup(res.text, 'lxml')


            #print(soup)
            #newslist = soup.select(".office_header")
            #print(len(newslist))
            
            ##뉴스업체
            #ofhd_float_title_text
            try:

                siteName = soup.find(class_="c_inner")
                siteName_val = siteName.text.split("ⓒ")[1].strip().split('.')[0].strip()
            except:
                continue
                #siteName_val = None
                #print(url)

            ##기사제목
            #media_end_head_headline
            try:
                title = soup.find(class_="media_end_head_headline")
                title_val = cleanText(title.text)
            except:
                continue
                #title_val = None
                #print(url)

            ##작성일자
            #media_end_head_info_datestamp_time _ARTICLE_DATE_TIME
            try:
                createDate = soup.find(class_="media_end_head_info_datestamp_time _ARTICLE_DATE_TIME")
                createDate_val = createDate.text
            except:
                continue
                #createDate_val = None
                #print(url)

            ##수정일자
            #media_end_head_info_datestamp_time _ARTICLE_MODIFY_DATE_TIME
            try:
                modifyDate = soup.find(class_="media_end_head_info_datestamp_time _ARTICLE_MODIFY_DATE_TIME")
                modifyDate_val = modifyDate.text
            except:
                modifyDate_val = None


            ##본문내용
            #dic_area 안 br카테고리 txt
            try:
                #text_list = ""

                brs = soup.find(id="dic_area")
                #print(len(brs))
                #brs = lis.findAll("br")
                #brs.findAll("br")

                text_list = cleanText(brs.get_text(strip=True))
                #for br in brs:
                #    text_list.append(br.get_text(strip=True))
                #print(text_list)
            except:
                print(url)


            ##이미지 URL
            #end_photo_org
            try:
                img_url_list = []

                urs = soup.findAll(class_="end_photo_org")
                #print(len(urs))
                for ur in urs:
                    img_url_list.append(ur.img['data-src'])
                #print(img_url_list)
            except:
                print(url)

            ##작성기자 기자 이메일
            #byline_s
            try:
                author_list = []

                authors = soup.findAll(class_="byline_s")
                #print(len(authors))
                for au in authors:
                    author_list.append(au.text)
                #print(author_list)
            except:
                print(url)

            # db연결
            db_connection = mysql.connector.connect(
                    host="shtestdb.duckdns.org",
                    user="hun",
                    port="13306",
                    password="12344321",
                    database="hun_test",
                )
            cursor = db_connection.cursor()


            if modifyDate_val != "":
                article_data = [
                    ( cat, url, siteName_val, title_val, str(' '.join(author_list)), createDate_val, modifyDate_val, text_list, str(' '.join(img_url_list))),
                    # 다른 기사 데이터도 추가
                    ]
            else:
                article_data = [
                    ( cat, url, siteName_val, title_val, str(' '.join(author_list)), createDate_val, modifyDate_val, text_list, str(' '.join(img_url_list))),
                    # 다른 기사 데이터도 추가
                    ]
            article_query = """
            INSERT IGNORE INTO Article (category_id, news_url, company_name, title, author_info, create_date, modify_date, content, image_url)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            
                    
            cursor.executemany(article_query, article_data)
            db_connection.commit()

            # 연결 종료
            cursor.close()
            db_connection.close()

            time.sleep(random.uniform(1.5,3.5))
            last_url[cat] = url

cats = [100, 101, 102, 103 ,104, 105]
last_url = {100:"",101:"",102:"",103:"",104:"",105:""}

while True:

    now = datetime.today().strftime('%Y%m%d')

    if today == now:
        url_lists = {}
        count = 0
        for cat in tqdm(cats):
            url_lists[cat] = make_urllist(cat, today)
            count += len(url_lists[cat])

        print(f"found new url : {count}")


        send_info(cats, url_lists)

    else:
        pass
        last_url = {}


    time.sleep(10)

    


"""/*
        if modifyDate_val != "":
         article_data = [
            ( cat, url, company_name, title, author_info, create_date, modify_date, news_contents, str(' '.join(image_url))),
            # 다른 기사 데이터도 추가
            ]
        else:
           article_data = [
            ( cat, url, company_name, title, author_info, create_date, None, news_contents, str(' '.join(image_url))),
            # 다른 기사 데이터도 추가
            ]

"""







