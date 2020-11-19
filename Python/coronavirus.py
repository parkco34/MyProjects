#!/usr/bin/env python3
import difflib
import re
import smtplib
import ssl
import time
from datetime import date, timedelta, datetime
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from io import StringIO
import numpy as np
import csv
import matplotlib.pyplot as plt
import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from df2gspread import df2gspread as d2g

# Interact with Google Drive API:
scope = ['https://www.googleapis.com/auth/drive.file']
credentials = ServiceAccountCredentials.from_json_keyfile_name('../client_secret.json', scope)
client = gspread.authorize(credentials)
gc = gspread.service_account()
sheet = gc.open("CoronaVirusTracker").sheet1
sheet = sheet.get_all_values()

spreadsheet_key = '1FMG7HFdBaZfwnQ4ub_ySbNlHhzSwRCCUb1buk8XDUJc'
wks_name = 'Master'
# Pycharm keyboard help: /\/\/\/\/\/\/\/\/\/\//\/\/\/\/\/\/\/\/\/\//\/\/\/\/\/\/\/\/\/\//\/\/\/\/\/\/\/
# run code: alt+shift+e
# Commenting: ctrl + /
# def replace_columns(df, new_columns):
#     k = 0
#     # for i in df.columns:
#     for i in x:
#         print('Old col', i, k)
#         # for j in new_columns:
#         for j in column_names:
#             seq = difflib.SequenceMatcher(None, i, j).ratio()*100
#             if seq >= 54:
#                 newcol = re.sub(i, j, i)
#                 # df.columns.values[k] = newcol
#                 x[k] = newcol
#                 k += 1
# What the hell was this for??:
# try:
#     waiting.until(EC.element_to_be_clickable((By.XPATH, '//*[@title="{}.csv"]'.format(path_to_click)))).click()
#     time.sleep(.5)
#     waiting.until(EC.element_to_be_clickable((By.XPATH, path_to_click))).click()
# except TimeoutException as ex:
#     # print("xpath: Something is going wrong at {}:".format(final_date) + str(ex))
#     time.sleep(.5)
#     raw = waiting.until(EC.element_to_be_clickable((By.XPATH, '/html/body/pre'))).text
#
# time.sleep(.5)
# driver.back()
# time.sleep(.5)
# driver.back()
# time.sleep(1)
# final_date = '04-25-2020'
# start_date = '02-24-2020'
start_date = '03-20-2020'
middle_date = '07-20-2020'
today = date.today()
todaystr = today.strftime('%m-%d-%Y')
yesterday = today - timedelta(days=1)
yesterday = yesterday.strftime('%m-%d-%Y')


def get_dates(start_date):
    date_i = datetime.strptime(start_date, '%m-%d-%Y')
    dates = pd.date_range(date_i, today - timedelta(days=1), freq='d')
    dates = pd.date_range(start_date, middle_date, freq='d')
    dates = dates.strftime('%m-%d-%Y')
    dates = dates.tolist()
    return dates


def replace_columns(df, new_columns):
    new_columns = sheet[0]

    k = 0
    for i in df.columns:
        print('Old col', i, k)
        for j in new_columns:
            seq = difflib.SequenceMatcher(None, i, j).ratio() * 100
            print(seq)
            if seq >= 54:
                newcol = re.sub(i, j, i)
                print("New column is ", newcol)
                if len(df.columns) == k:
                    # THIS BE WHERE DA FUCKIN ERROR OCCURS!
                    df.insert(k, newcol, np.nan)
                else:
                    df.columns.values[k] = newcol
                    k += 1
                # print("DFrame size is: ", df.columns.size)
def get_state_data(df, state):
    df = df.loc[df['Province_State'] == state]
    data = df[['Confirmed', 'Deaths', 'Recovered', 'Combined_Key']]

    if data.isnull().values.any():
        data = data.fillna(0)
    data['Confirmed'] = data['Confirmed'].astype(str).astype(int)
    data['Recovered'] = data['Recovered'].astype(str).astype(int)
    data['Deaths'] = data['Deaths'].astype(str).astype(int)

    _ = data.plot(figsize=(15, 5), subplots=False, title=state + ' ' + 'Rona')
    _ = plt.xlabel('Date')
    _ = plt.ylabel('Infected')
    plt.savefig('/home/parker/python/corona_initial.csv'.format(todaystr + ' ' + state))
    return data


# I need a function that will do this for me: If a column is added to raw data I'm scraping,
# add the new column and branch off to create new data frame and continue concatenating data
options = FirefoxOptions()
options.add_argument("--start-maximized")
# options.headless = True
# assert options.headless
def scrape(middle_date, path_to_click):
    ff_driver = "/usr/bin/geckodriver"
    site = "https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_daily_reports"
    driver = webdriver.Firefox(executable_path=ff_driver, options=options)
    driver.get(site)

    ignored_exceptions = (NoSuchElementException, StaleElementReferenceException)
    waiting = WebDriverWait(driver, 10, ignored_exceptions=ignored_exceptions)

    df = pd.DataFrame()

    for dt in get_dates(start_date):
        try:
            waiting.until(EC.element_to_be_clickable((By.XPATH, '//*[@title="{}.csv"]'.format(dt)))).click()
            time.sleep(.5)
            waiting.until(EC.element_to_be_clickable((By.XPATH, path_to_click))).click()
        except TimeoutException as ex:
            print("xpath: Something is going wrong at {}:".format(dt) + str(ex))

        time.sleep(.5)
        raw = waiting.until(EC.element_to_be_clickable((By.XPATH, '/html/body/pre'))).text
        raw_data = StringIO(raw)

        if dt != start_date:
            df2 = pd.read_csv(raw_data)
            replace_columns(df2, sheet[0])
            df2['Last_Update'] = pd.to_datetime(df2['Last_Update'])
            print(df2['Last_Update'])
            print('++++++++++++++++++++++++++++++++++++//')
            print(dt)
            print("++++++++++++++++++++++++++++++++++++")
            df = pd.concat([df, df2], axis=0, ignore_index=True)

        else:
            df1 = pd.read_csv(raw_data)
            replace_columns(df1, sheet[0])
            df1['Last_Update'] = pd.to_datetime(df1['Last_Update'])
            print(dt + '===========================================')
            print(df1['Last_Update'])
            print('===================================================/////////////////////')
            df = pd.concat([df, df1], axis=0, ignore_index=True)

        time.sleep(.5)
        print(dt)
        driver.back()
        time.sleep(.5)
        driver.back()
        time.sleep(.5)

    return df


# rona = scrape(yesterday, '//*[@id="raw-url"]')
# rona.to_csv('/home/parker/python/rona{}.csv'.format(final_date))
# }}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}
# What Date you wanna run this on?
rona = scrape(middle_date, '//*[@id="raw-url"]')
# }}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}
# CSV file from 2/2/2020 to 3/20/2020: /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\
# rona.to_csv('/home/parker/python/coronavirus_tracker/therona.csv', index=False)
# WHAT TEH FUCK????????!!!!!!!
# d2g.upload(rona, spreadsheet_key, wks_name, credentials=credentials, row_name=True)
# Set datetime index:
# rona['Last_Update'] = pd.to_datetime(rona['Last_Update']).dt.date  WHY????????????
# rona = rona.set_index('Last_Update')
# rona.reset_index(inplace=True)
# df_i = pd.read_csv(r'/home/parker/python/rona05-28-2020.csv')
# world = pd.concat([df_i, rona], axis=0, ignore_index=True)
# world['Last_Update'] = pd.to_datetime(world['Last_Update'])  # .dt.date
# world = world.set_index('Last_Update')
# world.index = pd.to_datetime(world.index)
# united_states = world.loc[world['Country_Region'] == 'US']
# Get Data:
# =============================================================================
# ny = get_state_data(world, 'New York')
# ca = get_state_data(world, 'California')
# tx = get_state_data(world, 'Texas')
# az = get_state_data(world, 'Arizona')
# wash = get_state_data(world, 'Washington')
# =============================================================================
# Send Email: /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\
# def send_it(state):
#     port = 465
#     sender_email = 'parkercorya@gmail.com'
#     # 'lparkerjr@yahoo.com',
#     if state == 'California':
#         send_to = ['dcp0426@sbcglobal.net', 'parkercorya@yahoo.com']
#
#     elif state == "Texas":
#         send_to = ['parkercorya@yahoo.com']
#
#     elif state == 'New York':
#         send_to = ['parkercorya@yahoo.com', ]
#
#     elif state == 'Washington':
#         send_to = "parkercorya@yahoo.com"
#
#     elif state == 'Arizona':
#         send_to = 'parkercorya@yahoo.com'
#
#     message = MIMEMultipart('alternative')
#     message['Subject'] = '! Corona Virus Update !'
#     message['From'] = sender_email
#     message['To'] = ", ".join(send_to)
#
#     text = """\
#         Hello friend,
#         This is an automatic email sent to you through my python script!!"""
#
#     html = """\
#         <html>
#             <body>
#                 <p>Hello friend,<br>
#                     Here's a link to the current global corona virus status:
#                     <a href="https://www.worldometers.info/coronavirus/">Corona Virus Info</a>
#                     <br>
#                     <hr>
#                 </p>
#                 <img src="https://media.giphy.com/media/Lq7TFOIexfjgkCsupk/giphy.gif" alt="gif failed to be shown">
#             </body>
#         </html>"""
#
#     # Turn these into plain/html MIMEText objects
#     part1 = MIMEText(text, 'plain')
#     part2 = MIMEText(html, 'html')
#     # The email client will try to render the last part first:
#     message.attach(part1)
#     message.attach(part2)
#
#     # DataFrame:
#     get_state_data(world, state)
#
#     img = open('.jpg'.format(todaystr + ' ' + state), 'rb')
#     msg_image = MIMEImage(img.read())
#     img.close()
#     msg_image.add_header('Content-ID', '<image1>')
#     message.attach(msg_image)
#
#     doc = open(r'')
#     password = doc.readline()
#     password = password[:-1]
#     doc.close()
#     context = ssl.create_default_context()
#     with smtplib.SMTP_SSL('smtp.gmail.com', port=port, context=context) as server:
#         server.login(sender_email, password)
#         server.sendmail(sender_email, send_to, message.as_string())
#
#
# send_it('New York')
# send_it('Texas')
# send_it('California')
# =============================================================================
# def send_time(time_to_send):
#     time.sleep(time_to_send.timestamp() - time.time())
#     send_it()
#     print('Your email has been sent...')
# 
# initial_time = pd.to_datetime(today)
# periodicity = timedelta(days=1)
# 
# time_to_send = initial_time
# while True:
#     send_time(time_to_send)
#     time_to_send = initial_time + periodicity
#
# 'Lauersdorf.michelle89@gmail.com'
# 'sfellows@sjfc.edu', 'jessica.parker0122@gmail.com','jpreston017@gmail.com', 'alisondoser@gmail.com', 
# 'Leaellenclayton@msn.com'
# =============================================================================
# =============================================================================
#     file = r'C:\Users\parkd\MyScripts\raw_data\Rona.jpg'
#     
#     with open(file, 'rb') as attachment:
#         part = MIMEBase('application', 'octet-stream')
#         part.set_payload(attachment.read())
#         
#     encoders.encode_base64(part)
#     
#     part.add_header(
#         "Content-Dispostion",
#         f"attachment; filename={file}",
#     )
#     
#     message.attach(part)
# =============================================================================
# /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/
