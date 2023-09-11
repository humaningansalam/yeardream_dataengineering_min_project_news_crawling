import mysql.connector
import pandas as pd
import os
import glob

folder_path = './data'

csv_files = glob.glob(os.path.join(folder_path, '*.csv'))

#for csv_file in csv_files:
#    print(csv_file)


for csv_file in csv_files:
    ##파일 읽기
    df = pd.read_csv(csv_file)

    cat = csv_file.split("/")[2].split("-")[0]
    #print(df)
    ##df읽기 테스트
    #for inx, row in df.iterrows():
    #    print(f"뉴스URL: {row['뉴스URL']}, 뉴스업체:{row['뉴스업체']}, 기사제목:{row['기사제목']}")
    
    for inx, row in df.iterrows():

        # MySQL 연결 설정
        db_connection = mysql.connector.connect(
            host="shtestdb.duckdns.org",
            user="hun",
            port="13306",
            password="12344321",
            database="hun_test",
        )

        # 커서 생성
        cursor = db_connection.cursor()


        if row['수정일자'] != "":
            # Article 테이블에 데이터 입력
            article_data = [
                ( cat, row['뉴스URL'], row['뉴스업체'], row['기사제목'], row['작성기자&이메일'], row['작성일자'], row['수정일자'], row['본문내용'], row['이미지URL']),
                # 다른 기사 데이터도 추가
            ]
        else:
            article_data = [
                ( cat, row['뉴스URL'], row['뉴스업체'], row['기사제목'], row['작성기자&이메일'], row['작성일자'], None, row['본문내용'], row['이미지URL']),
                # 다른 기사 데이터도 추가
            ]


        article_query = """
        INSERT INTO Article (category_id, news_url, company_name, title, author_info, create_date, modify_date, content, image_url)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        cursor.executemany(article_query, article_data)
        db_connection.commit()

        # 연결 종료
        cursor.close()
        db_connection.close()


