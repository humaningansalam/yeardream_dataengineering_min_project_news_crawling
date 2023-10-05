from datetime import datetime, timedelta

# 시작 날짜 설정 (예: 2023년 9월 1일)
start_date = datetime(2023, 9, 1)

# 오늘 날짜 구하기
end_date = datetime.now()

# 시작 날짜부터 오늘까지의 날짜 출력
current_date = start_date
print(current_date)

while current_date <= end_date:
    print(current_date.strftime("%Y%m%d"))
    current_date += timedelta(days=1)