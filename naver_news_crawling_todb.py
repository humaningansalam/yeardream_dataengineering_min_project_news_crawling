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






def make_urllist(code, date):
    page_num = 0
    urllist= []
    
    for i in range(10000):
        url = 'https://news.naver.com/main/list.nhn?mode=LSD&mid=sec&sid1='+str(code)+'&date='+str(date)+'&page='+str(i)
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.90 Safari/537.36'}
        news = requests.get(url, headers=headers)

        # BeautifulSoup의 인스턴스 생성합니다. 파서는 html.parser를 사용합니다.
        soup = BeautifulSoup(news.content, 'html.parser')

        # CASE 1
        news_list = soup.select('.newsflash_body .type06_headline li dl')
        # CASE 2
        news_list.extend(soup.select('.newsflash_body .type06 li dl'))
        
        # 각 뉴스로부터 a 태그인 <a href ='주소'> 에서 '주소'만을 가져옵니다.
        for line in news_list:
            urllist.append(line.a.get('href'))

        time.sleep(1)

        #뉴스 개수가 20개가 안되면 탈출
        if len(news_list) < 20:
            break;

    return urllist
    

cats = [100, 101, 102, 103 ,104, 105]

url_lists = {}
for cat in tqdm(cats):
    url_lists[cat] = make_urllist(cat, today)


# cat 값에 따라 url_list에 접근
for cat in tqdm(cats):
    #print(f"cat {i}: {url_lists[i]}")


    db_connection = mysql.connector.connect(
            host="shtestdb.duckdns.org",
            user="hun",
            port="13306",
            password="12344321",
            database="hun_test",
        )


    for url in url_lists[cat]:
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

        time.sleep(3)


    # 연결 종료
    cursor.close()
    db_connection.close()



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







