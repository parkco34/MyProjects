import pandas as pd
import datetime as dt
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

start_date = '02-24-2020'
final_date = '03-25-2020'
today = dt.datetime.now()
tdy = today.strftime('%m-%d-%Y')

def get_dateinterval(start_date, final_date):
    start_date = dt.datetime.strptime(start_date, '%m-%d-%Y')
    final_date = dt.datetime.strptime(final_date, '%m-%d-%Y')
    dates = pd.date_range(start_date, final_date, freq='d')
    dates = dates.strftime('%m-%d-%Y')
    dates = dates.tolist()
    return dates
# =============================================================================
# def get_dates(start_date):
#     start_date = dt.datetime.strptime(start_date, '%m-%d-%Y')
#     dates = pd.date_range(start_date, today - dt.timedelta(days=1),freq='d')
#     dates = dates.strftime('%m-%d-%Y')
#     dates = dates.tolist()
#     return dates
# =============================================================================

# Webscraping /\/\/\/\/\/\/\/\/\/\/\/\/\/\//\/\/\/\/\/\/\/\/\/\/\/\/\/\//\/\/\/\/\/\/\/\/\/\/\/\/\/\//\/\/\/\/\/\/\/\/\/\/\/\/\/\/
options = Options()
options.add_argument("--start-maximized")
options.headless = True
assert options.headless

#def scrape(start_date, final_date, path_to_click):
def scrape(start_date, final_date, path_to_click):
    chrome_driver = "C:/Users/parkd/MyScripts/chromedriver.exe"
    site = "https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_daily_reports"
    driver = webdriver.Chrome(executable_path=chrome_driver, options=options)
    driver.get(site)
    
    waiting = WebDriverWait(driver, 20)
    
#    for date in get_dates(start_date):
    for date in get_dateinterval(start_date, final_date):
        waiting.until(EC.element_to_be_clickable((By.XPATH, '//*[@title="{}.csv"]'.format(date)))).click()
        waiting.until(EC.element_to_be_clickable((By.XPATH, path_to_click))).click()
#        driver.find_element_by_xpath('/html/body/div[4]/div/main/div[2]/div/div[3]/div[1]/div[2]/div[1]/a[1]').click()
        raw = driver.find_element_by_xpath('/html/body/pre').text
        raw_data = StringIO(raw)
        
        if date == '02-24-2020':
 #       if date == '05-01-2020':
            df1 = pd.read_csv(raw_data)
        else:
            df2 = pd.read_csv(raw_data)
            rona_info = pd.concat([df1, df2], axis=0, ignore_index=True)

        driver.back()
        driver.back()    

    return rona_info

rona = scrape('02-24-2020', '03-25-2020', '/html/body/div[4]/div/main/div[2]/div/div[3]/div[1]/div[2]/div[1]/a[1]').to_csv('C:/Users/parkd/MyScripts/raw_data/Coronavirus_update {}.csv'.format(final_date), index=False)
#rona = scrape('05-01-2020', '/html/body/div[4]/div/main/div[2]/div/div[3]/div[1]/div[2]/div[1]/a[1]')

#df = pd.read_csv(r'C:\Users\parkd\MyScripts\raw_data\Coronavirus_update 04-30-2020.csv')
# Setting datetimeIndex:
# =============================================================================
# datetime = pd.to_datetime(df['Last_Update'])
# datetime_index = pd.DatetimeIndex(datetime.values)
# df = df.set_index(datetime_index)
# df.drop('Last_Update', axis=1, inplace=True)
# df.to_csv(r'C:\Users\parkd\MyScripts\raw_data\Coronavirus_update 04-30-2020.csv')
# =============================================================================

# MAKE DAILY AUTOMATIC: /\/\/\/\/\/\/\/\/\/\/\/\/\/\//\/\/\/\/\/\/\/\/\/\/\/\/\/\//\/\/\/\/\/\/\/\/\/\/\/\/\/\//\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/

#df = pd.concat([df, rona], axis=0, ignore_index=True)
# Data Analysis: /\/\/\/\/\/\/\/\/\/\/\/\/\/\//\/\/\/\/\/\/\/\/\/\/\/\/\/\//\/\/\/\/\/\/\/\/\/\/\/\/\/\//\/\/\/\/\/\/\/\/\/\/\/\/\/\/



# Send Email: /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\
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