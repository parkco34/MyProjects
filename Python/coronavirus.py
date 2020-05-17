import pandas as pd
import numpy as np
from datetime import date, timedelta, datetime
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from io import StringIO
import re
import difflib

#start_date = '04-26-2020'
final_date = '04-25-2020'
start_date = '02-24-2020'
today = date.today()
yesterday = today - timedelta(days=1)
yesterday = yesterday.strftime('%m-%d-%Y')

# =============================================================================
# def get_dateinterval(start_date, final_date):
#     start_date = strptime(start_date, '%m-%d-%Y')
#     final_date = strptime(yesterday, '%m-%d-%Y')
#     dates = pd.date_range(start_date, final_date, freq='d')
#     dates = dates.strftime('%m-%d-%Y')
#     dates = dates.tolist()
#     return dates
# =============================================================================
def get_dates(start_date):
    start_date = datetime.strptime(start_date, '%m-%d-%Y')
    dates = pd.date_range(start_date, today - timedelta(days=1), freq='d')
    dates = dates.strftime('%m-%d-%Y')
    dates = dates.tolist()
    return dates

def replace_cols(df, new_columns):
    k = 0
    for i in df.columns:
        for j in column_names:
            seq = difflib.SequenceMatcher(None,i, j).ratio()*100
            if seq >= 85:
                newcol = re.sub(i, j, i)
                df.columns.values[k] = newcol
#                print(newcol)
                k += 1

options = Options()
options.add_argument("--start-maximized")
options.headless = True
assert options.headless

column_names = ['FIPS','Admin2','Province_State','Country_Region','Last_Update','Lat','Long_','Confirmed','Deaths','Recovered','Active','Combined_Key']

def scrape(start_date, final_date, path_to_click):
    chrome_driver = "C:/Users/parkd/MyScripts/chromedriver.exe"
    site = "https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_daily_reports"
    driver = webdriver.Chrome(executable_path=chrome_driver, options=options)
    driver.get(site)
    
    waiting = WebDriverWait(driver, 20)
    
    df = pd.DataFrame(columns=column_names)

    for dt in get_dates(start_date):
        waiting.until(EC.element_to_be_clickable((By.XPATH, '//*[@title="{}.csv"]'.format(dt)))).click()
        waiting.until(EC.element_to_be_clickable((By.XPATH, path_to_click))).click()
        raw = driver.find_element_by_xpath('/html/body/pre').text
        raw_data = StringIO(raw)
        
        if date == start_date:
            df1 = pd.read_csv(raw_data)
            replace_cols(df1, column_names)
            df1['Last_Update'] = pd.to_datetime(df1['Last_Update'])
            df = pd.concat([df, df1], axis=0, ignore_index=True)
        else:
            df2 = pd.read_csv(raw_data)
            replace_cols(df2, column_names)
            df2['Last_Update'] = pd.to_datetime(df2['Last_Update'])
            df = pd.concat([df, df2], axis=0, ignore_index=True)

        driver.back()
        driver.back()    

    return df

rona = scrape(start_date, final_date, '/html/body/div[4]/div/main/div[2]/div/div[3]/div[1]/div[2]/div[1]/a[1]')
rona.to_csv('C:/Users/parkd/MyScripts/raw_data/Coronavirus_update {}.csv'.format(final_date), index=False)

#!=> Get rid of latitude and longitude columns!

# Setting datetimeindex:
df_i = pd.read_csv(r'C:\Users\parkd\MyScripts\raw_data\Coronavirus 03-25 to 04-26 2020.csv')
df_f = pd.concat([df_i, rona], axis=0, ignore_index=True)
df_f['Last_Update'] = pd.to_datetime(df_f['Last_Update'])
df_f = df_f.set_index('Last_Update')

# Data Analysis: /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\//\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\//\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\//\/\/\/\/\/\/\/\/\/\/\
ny = df_f[df_f['Province_State'] == 'New York']


# MAKE DAILY AUTOMATIC: /\/\/\/\/\/\/\/\/\/\/\/\/\/\//\/\/\/\/\/\/\/\/\/\/\/\/\/\//\/\/\/\/\/\/\/\/\/\/\/\/\/\//\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/


# Send Email: /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/
# =============================================================================
# def sendit():
#     port = 465
#     sender_email = 'parkercorya@gmail.com'
#     send_to = ['parkdaddy34@gmail.com', 'parkercorya@yahoo.com']
# #    receiver_email = ['jessica.parker0122@gmail.com', 'Lauersdorf.michelle89@gmail.com', 'jpreston017@gmail.com']
#     message = MIMEMultipart('alternative')
#     message['Subject'] = '! Corona Virus Update !'
#     message['From'] = sender_email
#     message['To'] = ", ".join(send_to)
#     
#     text = """\
#         Hello Cunt,
#         I'm emailing you through my python script!!"""
#         
#     html = """\
#         <html>
#             <body>
#                 <p>Hello Cunt,<br>
#                     Here's a link to the current global corona virus status:
#                     <a href="https://www.worldometers.info/coronavirus/">Corona Virus Info</a>
#                 </p>
#                 <img src="https://media.giphy.com/media/Lq7TFOIexfjgkCsupk/giphy.gif" alt="gif failed to be shown">
#             </body>
#         </html>
#         """
#     
#     # Turn these into plain/html MIMEText objects
#     part1 = MIMEText(text, 'plain')
#     part2 = MIMEText(html, 'html')
#     # The email client will try to render the last part first:
#     message.attach(part1)
#     message.attach(part2)
# 
# 
#     password = 'rqlxrhcqpmsjpbfr'
#     context = ssl.create_default_context()
#     with smtplib.SMTP_SSL('smtp.gmail.com', port=port, context=context) as server:
#         server.login('parkercorya@gmail.com', password)
# 
# def send_time(time_to_send):
#     time.sleep(time_to_send.timestamp() - time.time())
#     sendit()
#     print('Your email has been sent...')
# 
# initial_time = dt.datetime(2020, 3, 30, 11, 25)
# periodicity = dt.timedelta(days=1)
# 
# time_to_send = initial_time
# while True:
#     send_time(time_to_send)
#     time_to_send = initial_time + periodicity
# =============================================================================


#/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\