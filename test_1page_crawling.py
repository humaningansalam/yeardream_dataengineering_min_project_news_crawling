import requests
from bs4 import BeautifulSoup
import json
import pandas as pd

columns = {
    '뉴스URL': [],
    '뉴스업체': [],
    '기사제목': [],
    '작성일자': [],
    '본문내용': [],
    '이미지URL': [],
    '작성기자&이메일': []
}

df = pd.DataFrame(columns)
print(df)


url = "https://n.news.naver.com/article/025/0003304134"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"}

res = requests.get(url, headers=headers)
soup = BeautifulSoup(res.text, 'lxml')


#print(soup)
#newslist = soup.select(".office_header")
#print(len(newslist))


##뉴스업체
#ofhd_float_title_text
#siteName = soup.find(class_="ofhd_float_title_text")
#print(siteName.text)
#c_inner
siteName = soup.find(class_="c_inner")
print(siteName.text.split("ⓒ")[1].strip().split('.')[0].strip())


##기사제목
#media_end_head_headline
title = soup.find(class_="media_end_head_headline")
print(title.text)


##작성일자
#media_end_head_info_datestamp_bunch
createDate = soup.find(class_="media_end_head_info_datestamp_time _ARTICLE_DATE_TIME")
print(createDate.text)

##수정일자
#media_end_head_info_datestamp_bunch
modifyDate = soup.find(class_="media_end_head_info_datestamp_time _ARTICLE_MODIFY_DATE_TIME")
print(modifyDate.text)


##본문내용
#dic_area 안 br카테고리 txt
brs = soup.find(id="dic_area")
#print(len(brs))
#brs = lis.findAll("br")
#brs.findAll("br")
text_list = []
for br in brs:
    text_list.append(br.get_text(strip=True))

print(text_list)


##이미지 URL
#end_photo_org
urs = soup.findAll(class_="end_photo_org")
#print(len(urs))
img_url_list = []
for ur in urs:
    img_url_list.append(ur.img['data-src'])

print(img_url_list)



##작성기자 기자 이메일
#byline_s
authors = soup.findAll(class_="byline_s")
#print(len(authors))
author_list = []
for au in authors:
    author_list.append(au.text)
print(author_list)



new_row = {
    '뉴스URL': url,
    '뉴스업체': siteName.text.split("ⓒ")[1].strip().split('.')[0].strip(),
    '기사제목': title.text,
    '작성일자': createDate.text,
    '수정일자': modifyDate.text,
    '본문내용': text_list,
    '이미지URL': img_url_list,
    '작성기자&이메일': author_list,
}
new_row_df = pd.DataFrame([new_row], columns=columns)

df = pd.concat([df,new_row_df], ignore_index=True)


df.to_csv("1pagetest.csv", encoding="utf-8-sig")





















## 댓글정보수집
"""
comment = soup.findAll(id_="u_cbox_area")
print(len(comment))
print(comment.text())


news_company = "025"
num_ = "0003304134"

news_id =  "news" + news_company + ","+ num_ 

#url_ori = 'https://apis.naver.com/commentBox/cbox/web_naver_list_jsonp.json?ticket=news&templateId=view_society&pool=cbox5&_wr&_callback=jQuery11240673401066245984_1638166575411&lang=ko&country=KR&objectId=' + news_id + '&categoryId=&pageSize=10&indexSize=10&groupId=&listType=OBJECT&pageType=more&page=1&initialize=true&userType=&useAltSort=true&replyPageSize=20&sort=favorite&includeAllStatus=true&_=1638166575413'



oid = "025"
aid = "0003304134"

page = "1"


url_ori = "https://apis.naver.com/commentBox/cbox/web_neo_list_jsonp.json?ticket=news&templateId=default_society&pool=cbox5&_callback=jQuery1707138182064460843_1523512042464&lang=ko&country=&objectId=news"+oid+"%2C"+aid+"&categoryId=&pageSize=20&indexSize=10&groupId=&listType=OBJECT&pageType=more&page="+str(page)+"&refresh=false&sort=FAVORITE" 


url_news =  url_ori
res = requests.get(url_news, headers=headers)
reply_json = json.loads(res.text[res.text.find('{'):-2])


print(reply_json)
## 성별 통계정보 가져오기
gender_male   = reply_json['result']['graph']['gender']['male']
gender_female = reply_json['result']['graph']['gender']['female']

print(gender_male)

## 연령 통게정보 가져오기
ages_group_10 = reply_json['result']['graph']['old'][0]['value']
ages_group_20 = reply_json['result']['graph']['old'][1]['value']
ages_group_30 = reply_json['result']['graph']['old'][2]['value']
ages_group_40 = reply_json['result']['graph']['old'][3]['value']
ages_group_50 = reply_json['result']['graph']['old'][4]['value']
ages_group_60 = reply_json['result']['graph']['old'][5]['value']
ages_group_60 = reply_json['result']['graph']['old'][5]['value']
"""