from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from random import randint
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time
import calendar
import requests
import re
import pymysql
import uuid
import numpy as np
import sys
import shutil


# slack
# 다 삭제함
options = Options()
options.add_argument("--headless")  # AWS에서는 보통 headless 모드 필요
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--user-data-dir=/tmp/chrome-user-data")  # 고유한 데이터 디렉토리 설정


start_time = time.time()
mongddang_list= []
today = str(datetime.today())[:10]
today_year = today.split("-")[0]
last_day_of_month = calendar.monthrange(int(today.split("-")[0]), 12)[1]
url_num_list = []


for i in range(1,3):
    res = requests.get(f"https://youth.seoul.go.kr/infoData/sprtInfo/list.do?sprtInfoId=&key=2309130006&pageIndex={i}&orderBy=regYmd+desc&recordCountPerPage=8&sc_ctgry=&sw=&sc_rcritCurentSitu=%EC%83%81%EC%8B%9C&sc_rcritCurentSitu=%EB%AA%A8%EC%A7%91%EC%A4%91&sc_rcritCurentSitu=%EB%AA%A8%EC%A7%91%EC%98%88%EC%A0%95&viewType=on&sc_aplyPrdEndYmdUseYn=&cntrLa=37.566761128870546&cntrLo=126.97862963872868&neLat=37.566761128870546&neLng=126.97862963872868&swLat=37.566761128870546&swLng=126.97862963872868&mapLvl=6&sarea=")
    soup = BeautifulSoup(res.content, "html.parser")
    elems = soup.select("a.item-overlay")
    
    for elem in elems:
        page_num = elem["onclick"]
        page_num = page_num.split("(")[1][1:6]
        url_num_list.append(page_num)
        detail_url = f"https://youth.seoul.go.kr/infoData/sprtInfo/view.do?sprtInfoId={page_num}&key=2309130006&pageIndex=1&orderBy=regYmd+desc&recordCountPerPage=8&sc_ctgry=PDS_08_YC&sw=&sc_rcritCurentSitu=%EC%83%81%EC%8B%9C&sc_rcritCurentSitu=%EB%AA%A8%EC%A7%91%EC%A4%91&sc_rcritCurentSitu=%EB%AA%A8%EC%A7%91%EC%98%88%EC%A0%95&viewType=on&sc_aplyPrdEndYmdUseYn=&cntrLa=37.566761128870546&cntrLo=126.97862963872868&neLat=37.566761128870546&neLng=126.97862963872868&swLat=37.566761128870546&swLng=126.97862963872868&mapLvl=6&sarea="


# chroem_driver Headless 관련 정의
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument('--window-size=1920,1080')
chrome_options.add_argument("--headless")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
service=ChromeService(ChromeDriverManager().install())
print(service.path)
mongddang_list= []
start_time = time.time()
driver = webdriver.Chrome(options=options)
today = str(datetime.today())[:10]
today_year = today.split("-")[0]
last_day_of_month = calendar.monthrange(int(today.split("-")[0]), 12)[1]

for url in url_num_list:
    try:
        driver.get(f"https://youth.seoul.go.kr/infoData/sprtInfo/view.do?sprtInfoId={url}&key=2309130006&pageIndex=1&orderBy=regYmd+desc&recordCountPerPage=8&sc_ctgry=PDS_08_YC&sw=&sc_rcritCurentSitu=%EC%83%81%EC%8B%9C&sc_rcritCurentSitu=%EB%AA%A8%EC%A7%91%EC%A4%91&sc_rcritCurentSitu=%EB%AA%A8%EC%A7%91%EC%98%88%EC%A0%95&viewType=on&sc_aplyPrdEndYmdUseYn=&cntrLa=37.566761128870546&cntrLo=126.97862963872868&neLat=37.566761128870546&neLng=126.97862963872868&swLat=37.566761128870546&swLng=126.97862963872868&mapLvl=6&sarea=")
        time.sleep(1)
        current_url = driver.current_url
        idx = "MONGDDANG" + str(current_url.split("sprtInfoId=")[1].split("&")[0])
        title = driver.find_element(By.XPATH,"//*[@id='frm']/div/div[1]/div[2]/div[1]/strong").text
        title = title[:-2].strip() if title.endswith("안내") else title
        detail_link = driver.find_element(By.CSS_SELECTOR, "div.btn-group a").get_attribute('href')
        print(detail_link)

        if detail_link == "https://youth.seoul.go.kr/infoData/sprtInfo/www.jbedu.or.kr":
            detail_link = "https://www.jbedu.or.kr"
            print(detail_link)


        apply_date = driver.find_element(By.XPATH, "//*[@id='frm']/div/div[1]/div[2]/ul[1]/li[1]").text
        apply_date = apply_date.split("\n")[1]

        detail_support = driver.find_element(By.XPATH, "//*[@id='frm']/div/div[2]/div[1]")

        if detail_support:
            detail_support = detail_support.text
            detail_support = "○ " + detail_support.replace("상세정보","")
        else:
            detail_support = None

        # 현재 날짜를 가져옴
        today_time = datetime.now().strftime('%Y-%m-%d')
        if "상시" in apply_date:
            last_year = str(today_time)[:4]
            last_day = str(calendar.monthrange(int(str(today_time).split("-")[0]), int(str(today_time).split("-")[1]))[1])
            apply_date = today_time + " ~ " + last_year + "-12-" + str(last_day_of_month)

        try:
            ongoing_time = driver.find_element(By.XPATH, "//*[@id='frm']/div/div[1]/div[2]/ul[1]/li[2]").text
            ongoing_time = ongoing_time.split("\n")[1]
            if "상시" in ongoing_time:
                last_year = str(datetime.today())[:4]
                last_day = str(calendar.monthrange(int(str(today_time).split("-")[0]), int(str(today_time).split("-")[1]))[1])
                ongoing_time = today_time + " ~ " + last_year + "-12-" + str(last_day_of_month)
        except:
            pass

        target = driver.find_element(By.XPATH, "//*[@id='frm']/div/div[1]/div[2]/ul[1]/li[3]").text
        if len(target.split("\n")) > 1:
            target = "○ " + target.split("\n")[1]
        else:
            target = None
        policy_name = driver.find_element(By.XPATH, "//*[@id='frm']/div/div[1]/div[2]/ul[1]/li[4]").text
        policy_name = policy_name.split("\n")[1]

        wello_list = [idx,title,detail_support,apply_date,ongoing_time,target,policy_name,current_url, detail_link]
        mongddang_list.append(wello_list)
        print("data_append success..!!")
    except:
        continue

df = pd.DataFrame(data = mongddang_list, columns = ["번호","공고명","상세지원내용","신청기간","진행일정","대상","담당기관","링크","상세링크"])
# 공고명 전처리
emoji_pattern = re.compile("["
                           "\U0001F600-\U0001F64F"  # 스마일리 페이스
                           "\U0001F300-\U0001F5FF"  # 활성화된 스마일리 페이스
                           "\U0001F680-\U0001F6FF"  # 트랜스포트 및 심볼
                           "\U0001F1E0-\U0001F1FF"  # 나라 국기(1)
                           "\U0001F191-\U0001F251"  # 나라 국기(2)
                           "]+", flags=re.UNICODE)
    
df["공고명"] = df["공고명"].apply(lambda x : emoji_pattern.sub(r'', x))


# 날짜 범위를 추출하는 함수
def extract_date_range(apply_date):
    # 유효한 날짜 범위를 추출하는 패턴 정의.
    pattern = r'(\d{4}-\d{2}-\d{2} ~ \d{4}-\d{2}-\d{2})(?: \d{2} : \d{2})?(?: \[ 선착순 마감 \])?'
    
    # 정규 표현식으로 패턴 매칭
    match = re.search(pattern, apply_date)
    
    if match:
        # 첫 번째 캡처 그룹 (날짜 범위만)을 반환
        return match.group(1)
    
    # 매칭되지 않으면 None 반환
    return None


def extract_date(ongoing_date):
    match = re.search(r'\d{4}-\d{2}-\d{2}', ongoing_date)
    if match:
        return match.group(0)
    else:
        return None
        

def preprocess_row(row):
    if row["전처리된_신청기간"] == None:
        try:
            calend_date = (pd.to_datetime(row["진행일정"][:10]) - timedelta(days=1)).strftime("%Y-%m-%d")
            return f"{calend_date} ~ {calend_date}"
        except:
            pass
    else:
        return row["전처리된_신청기간"]
    
    
    
today = str(datetime.today())[:10]
today_year = today.split("-")[0]
last_day_of_month = calendar.monthrange(int(today.split("-")[0]), 12)[1]
print(today_year)


# 상세지원내용 전처리

df["상세지원내용"] = df["상세지원내용"].apply(lambda x: ' '.join(re.findall(r"[a-zA-Z0-9가-힣]+", x)))


df["전처리된_신청기간"] = df["신청기간"].apply(lambda x : extract_date_range(x))
df["전처리된_신청기간"] = df.apply(preprocess_row, axis=1)
df["전처리된_신청기간"] = df.apply(preprocess_row, axis=1)
df["전처리된_신청기간"] = df["전처리된_신청기간"].apply(lambda x : today + " ~ " + str(today_year) + "-12-" + str(last_day_of_month) if x is None else x)
df["신청기간_타입"] = df["신청기간"].apply(
    lambda x: "C15-03" if "선착순" in  x else "C15-06"
)


df["전처리된_진행일정"] = df["진행일정"].apply(lambda x : extract_date_range(x))
df["전처리된_진행일정_1"] = df["진행일정"].apply(lambda x : extract_date(x))

tmp_extract = []
for cond_1, cond_2 in zip(df["전처리된_진행일정"], df["전처리된_진행일정_1"]):
    if cond_2 == None:
        cond_2 = str(datetime.today())[:10]
    if cond_1 == None:
        cond_1 = cond_2
        tmp_extract.append(cond_1)
        
     
df.loc[df["전처리된_진행일정"].isna(), "전처리된_진행일정"] = tmp_extract

df["전처리된_진행일정"] = df["전처리된_진행일정"].apply(lambda x : x + " ~ " + x if "~" not in x else x)

# 신청기간 시작일짜, 끝날짜 나누기
df["전처리된_신청기간_시작일자"] = df["전처리된_신청기간"].apply(lambda x : x.split("~")[0])
df["전처리된_신청기간_끝날짜"] = df["전처리된_신청기간"].apply(lambda x : x.split("~")[1])

# 진행일정 시작일자, 끝날짜 나누기
df["전처리된_진행일정_시작일자"] = df["전처리된_진행일정"].apply(lambda x : x.split("~")[0])
df["전처리된_진행일정_끝날짜"] = df["전처리된_진행일정"].apply(lambda x : x.split("~")[1])

# 담당기관 전처리
df["담당기관"] = df["담당기관"].apply(lambda x : re.sub("[()기타]", "", x))

df = df[["번호","공고명","상세지원내용","신청기간","전처리된_신청기간_시작일자","전처리된_신청기간_끝날짜", \
        "신청기간_타입","전처리된_진행일정","대상","담당기관","링크","상세링크"]]
my_wello_df = df.copy(deep = True)
# my_wello_df = df[pd.to_datetime(df["전처리된_신청기간_끝날짜"]) > datetime.today()]

# 폴리시 타입 cd 로
#B2C_RSS_POLICY_TYPE_APPLICATION 신청형
#B2C_RSS_POLICY_TYPE_INFORMATION 안내형
#B2C_RSS_POLICY_TYPE_NON_BENEFIT 비수혜성
#B2C_RSS_POLICY_TYPE_PARTICIPATION 참여형
# Converting and mapping columns


# 데이터 프레임 정의
convert_my_wello_df = pd.DataFrame()
convert_my_wello_df["policy_name"] = my_wello_df["공고명"]
convert_my_wello_df["agency"] = my_wello_df["담당기관"].apply(lambda x: x.strip())
convert_my_wello_df["age_begin"] = 0
convert_my_wello_df["age_end"] = 99
convert_my_wello_df["income_begin"] = 0
convert_my_wello_df["income_end"] = 99999
convert_my_wello_df["administrative_rules"] = None
convert_my_wello_df["agency_apply"] = my_wello_df["담당기관"].apply(lambda x: x.strip())
convert_my_wello_df["agency_tel"] = None
convert_my_wello_df["apply_documents"] = None
convert_my_wello_df["apply_url"] = None
convert_my_wello_df["base_rule"] = None
convert_my_wello_df["department"] = my_wello_df["담당기관"].apply(lambda x: x.strip())
convert_my_wello_df["desc_age"] = None
convert_my_wello_df["desc_apply"] = None
convert_my_wello_df["desc_criteria"] = my_wello_df["대상"]
convert_my_wello_df["desc_service"] = None
convert_my_wello_df["desc_support"] = None
convert_my_wello_df["desc_target"] = None
convert_my_wello_df["due_date_begin"] = my_wello_df["전처리된_신청기간_시작일자"]
convert_my_wello_df["due_date_end"] = my_wello_df["전처리된_신청기간_끝날짜"]
convert_my_wello_df["gov_service_id"] = my_wello_df["번호"]
convert_my_wello_df["info_url"] = my_wello_df["상세링크"]
# convert_my_wello_df["origin_url"] = my_wello_df["링크"]
convert_my_wello_df["local_gevernments_rules"] = None
convert_my_wello_df["priority"] = 16
convert_my_wello_df["inspection_status"] = "INSPECTION_STATUS_LABELLING"
convert_my_wello_df["policy_type_cd"] = "B2C_RSS_POLICY_TYPE_PARTICIPATION"
convert_my_wello_df["support_benefit"] = None
convert_my_wello_df["origin_policy_name"] = my_wello_df["공고명"]
# convert_my_wello_df["avail_delete_yn"] = "Y"
convert_my_wello_df["labeler_id"] = None
convert_my_wello_df["code_due_date_type"] = my_wello_df["신청기간_타입"]
convert_my_wello_df["agency_type"] = None
convert_my_wello_df["desc_provision"] = None
convert_my_wello_df["origin"] = "청년몽땅 정보통"
convert_my_wello_df["code_agency"] = None
convert_my_wello_df["id_idx"] = my_wello_df["번호"]
convert_my_wello_df["display_yn"] = "Y"
convert_my_wello_df["non_display_reason"] = None
convert_my_wello_df["create_at"] = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
convert_my_wello_df["create_id"] = 0
convert_my_wello_df["update_id"] = 0
convert_my_wello_df["code"] = "C08-04"
convert_my_wello_df["root_code"] = "C08"
convert_my_wello_df["level"] = 2  # 기본값 설정
print(convert_my_wello_df["info_url"])

# DataFrame을 반복하여 조건에 따라 'code' 및 'root_code' 컬럼을 업데이트.
for index, value in enumerate(convert_my_wello_df["agency"].values):
    if value is not None and len(value) >= 1:
        if value[-1] in ["시", "군", "구"]:
            convert_my_wello_df.loc[index, "code"] = "C08-04"
            convert_my_wello_df.loc[index, "root_code"] = "C08"
        else:
            convert_my_wello_df.loc[index, "code"] = "C08-04"
            convert_my_wello_df.loc[index, "root_code"] = "C08"

# Reordering the columns as per the given order
ordered_columns = ["policy_name", "agency", "age_begin", "age_end", "income_begin", "income_end", 
                   "administrative_rules", "agency_apply", "agency_tel", "apply_documents", "apply_url", 
                   "base_rule", "department", "desc_age", "desc_apply", "desc_criteria", "desc_service", 
                   "desc_support", "desc_target", "due_date_begin", "due_date_end", "gov_service_id", "info_url",
                   "local_gevernments_rules", "priority", "inspection_status", "policy_type_cd", "support_benefit", 
                   "origin_policy_name", "labeler_id", "code_due_date_type", "agency_type", 
                   "desc_provision", "origin", "code_agency", "id_idx", "display_yn", "non_display_reason", 
                   "create_at", "create_id", "update_id", "code", "root_code", "level"]

# Ensure the dataframe has the correct columns
convert_my_wello_df = convert_my_wello_df[ordered_columns]
convert_my_wello_df = convert_my_wello_df.replace({np.nan: None})

# Verify the number of columns
print(f"Number of columns: {len(convert_my_wello_df.columns)}")  # Should match the number of columns in the table

# Database connection
host = "localhost"
user = "root"
password = "0000"
database = "wello_data"

connection = pymysql.connect(
    host=host,
    user=user,
    password=password,
    database=database
)

if connection:
    print("데이터 베이스 연결 성공 !!")
cnt = 0
try:
    with connection.cursor() as cursor:
        for row_data_num, row_each_data in enumerate(convert_my_wello_df.values):
            # Select query to check for existing record
            select_query = """
                SELECT * FROM meta_policy 
                WHERE policy_name = %s AND gov_service_id = %s
            """
            cursor.execute(select_query, (row_each_data[0], row_each_data[21]))  # 중복데이터 스킵
            result = cursor.fetchone()
            if result:
                print(f"Skipping duplicate entry for gov_service_id:{row_each_data[21]} and policy_name: {row_each_data[0]}")
                continue

            # Insert query
            insert_query = """
            INSERT IGNORE INTO wello_data.meta_policy (
                `policy_name`, `agency`, `age_begin`, `age_end`, `income_begin`, 
                `income_end`, `administrative_rules`, `agency_apply`, `agency_tel`, `apply_documents`, 
                `apply_url`, `base_rule`, `department`, `desc_age`, `desc_apply`, 
                `desc_criteria`, `desc_service`, `desc_support`, `desc_target`, `due_date_begin`, 
                `due_date_end`, `gov_service_id`, `info_url`,`local_gevernments_rules`, `priority`, 
                `inspection_status`, `policy_type_cd`, `support_benefit`, 
                `origin_policy_name`, `labeler_id`, `code_due_date_type`, `agency_type`, 
                `desc_provision`, `origin`, `code_agency`, `id_idx`, `display_yn`, 
                `non_display_reason`, `create_at`, `create_id`
            )
            VALUES (
                %s,%s,%s,%s,%s,
                %s,%s,%s,%s,%s,
                %s,%s,%s,%s,%s,
                %s,%s,%s,%s,%s,
                %s,%s,%s,%s,%s,
                %s,%s,%s,
                %s,%s, %s, %s,%s,
                %s,%s,%s,%s,%s,
                %s, %s
            )
            """
            values = (
                row_each_data[0], row_each_data[1], row_each_data[2], row_each_data[3], row_each_data[4],
                row_each_data[5], row_each_data[6], row_each_data[7], row_each_data[8], row_each_data[9],
                row_each_data[10], row_each_data[11], row_each_data[12], row_each_data[13], row_each_data[14],
                row_each_data[15], row_each_data[16], row_each_data[17], row_each_data[18], row_each_data[19],
                row_each_data[20], row_each_data[21], row_each_data[22], row_each_data[23], row_each_data[24],
                row_each_data[25], row_each_data[26], row_each_data[27], row_each_data[28], row_each_data[29],
                row_each_data[30], row_each_data[31], row_each_data[32], row_each_data[33], row_each_data[34],
                row_each_data[35], row_each_data[36], row_each_data[37], row_each_data[38], row_each_data[39]
                
            )
            cursor.execute(insert_query, values)
            connection.commit()
            # 중복이 아니면
            cnt += 1
            print("data insert 성공")
            # Fetch the last inserted meta_policy_id for this row
            # meta_policy_id = cursor.lastrowid

            # Ensure the meta_policy_id was inserted successfully
            # if meta_policy_id:
            #     lastroid_insert_query = """
            #     INSERT INTO meta_policy_code (
            #         code, root_code, meta_policy_id, level
            #     )
            #     VALUES (%s, %s, %s, %s)
            #     """
            #     lastroid_values = (
            #         row_each_data[41],
            #         row_each_data[42], 
            #         meta_policy_id,
            #         row_each_data[43]  # 기본값을 2로 설정
            #     )
            #     cursor.execute(lastroid_insert_query, lastroid_values)
            #     # 중복데이터가 아니면 추가
            #     cnt += 1
            #     print("data insert 성공")

            #     # Insert into meta_policy_crawling table
            #     crawling_insert_query = """
            #     INSERT INTO meta_policy_crawling (
            #         meta_policy_id, policy_name
            #     )
            #     VALUES (%s, %s)
            # #     """
            #     crawling_values = (
            #         meta_policy_id,
            #         row_each_data[0]
            #     )
            #     cursor.execute(crawling_insert_query, crawling_values)
            #     connect.commit()
            #     # 중복 데이터가 아니면 += 1
            #     cnt += 1
            #     print("Data inserted successfully!")
except:
    pass


