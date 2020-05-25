import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import date, timedelta, datetime
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from io import StringIO
import re
import difflib


#final_date = '04-25-2020'
#start_date = '02-24-2020'
start_date = '04-26-2020'
today = date.today()
todaystr = today.strftime('%m-%d-%Y')
yesterday = today - timedelta(days=1)
yesterday = yesterday.strftime('%m-%d-%Y')


def get_dates(start_date, final_date):
    start_date = datetime.strptime(start_date, '%m-%d-%Y')
    dates = pd.date_range(start_date, today - timedelta(days=1), freq='d')
    dates = pd.date_range(start_date, final_date, freq='d')
    dates = dates.strftime('%m-%d-%Y')
    dates = dates.tolist()
    return dates

def replace_columns(df, new_columns):
    k = 0
    for i in df.columns:
        #print('Old col', i, k)
        for j in column_names:
            seq = difflib.SequenceMatcher(None,i, j).ratio()*100
            if seq >= 54:
                newcol = re.sub(i, j, i)
                #print('Newcol ', newcol)
                df.columns.values[k] = newcol
                k += 1
                
def get_state_data(df, state):
    df = df.loc[df['Province_State'] == state]
    data = df[['Confirmed', 'Deaths', 'Recovered', 'Combined_Key']]
    
    if data.isnull().values.any():
        data = data.fillna(0)
    data['Confirmed'] = data['Confirmed'].astype(str).astype(int)
    data['Recovered'] = data['Recovered'].astype(str).astype(int)
    data['Deaths'] = data['Deaths'].astype(str).astype(int)
    
    _ = data.plot(figsize=(15,5), subplots=False, title= state + ' ' + 'Rona')
    _ = plt.xlabel('Date')
    _ = plt.ylabel('Infected')
    plt.savefig(r'C:\Users\parkd\MyScripts\raw_data\Rona{}.jpg'.format(todaystr+' '+state))
    return data
    # Latest Data: =====================================================================>>>>>>>>>>>>>>>>>>>>>>>>>> WORK ON THIS!!
# =============================================================================
#     yester = datetime.strptime(yesterday, '%m-%d-%Y')
#     yester = yester.date()
#     current_df = data[]
# =============================================================================

column_names = ['FIPS','Admin2','Province_State','Country_Region','Last_Update','Lat','Long_','Confirmed','Deaths','Recovered','Active','Combined_Key']

def scrape(start_date, final_date, path_to_click):
    chrome_driver = "C:/Users/parkd/MyScripts/chromedriver.exe"
    site = "https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_daily_reports"
    driver = webdriver.Chrome(executable_path=chrome_driver, options=options)
    driver.get(site)
    
    waiting = WebDriverWait(driver, 20)
    
    df = pd.DataFrame(columns=column_names)

    #for dt in get_dates(start_date, final_date):
    for dt in get_dates(start_date, yesterday):
        waiting.until(EC.element_to_be_clickable((By.XPATH, '//*[@title="{}.csv"]'.format(dt)))).click()
        waiting.until(EC.element_to_be_clickable((By.XPATH, path_to_click))).click()
        raw = driver.find_element_by_xpath('/html/body/pre').text
        raw_data = StringIO(raw)
        
        if dt == start_date:
            df1 = pd.read_csv(raw_data)
            replace_columns(df1, column_names)
            df1['Last_Update'] = pd.to_datetime(df1['Last_Update'])
            df = pd.concat([df, df1], axis=0, ignore_index=True)
        else:
            df2 = pd.read_csv(raw_data)
            replace_columns(df2, column_names)
            df2['Last_Update'] = pd.to_datetime(df2['Last_Update'])
            df = pd.concat([df, df2], axis=0, ignore_index=True)

        driver.back()
        driver.back()

    return df

options = Options()
options.add_argument("--start-maximized")
options.headless = True
assert options.headless

rona = scrape(start_date, yesterday, '/html/body/div[4]/div/main/div[2]/div/div[3]/div[1]/div[2]/div[1]/a[1]')
#rona.to_csv('C:/Users/parkd/MyScripts/raw_data/Coronavirus_update {}.csv'.format(yesterday))

# Set datetimeindex:
#rona['Last_Update'] = pd.to_datetime(rona['Last_Update']).dt.date  WHY?????????????///

rona = rona.set_index('Last_Update')
rona.reset_index(inplace=True)
df_i = pd.read_csv(r'C:\Users\parkd\MyScripts\raw_data\Coronavirus_update 04-25-2020.csv')
world = pd.concat([df_i, rona], axis=0, ignore_index=True)
world['Last_Update'] = pd.to_datetime(world['Last_Update'])#.dt.date
world = world.set_index('Last_Update')
world.index = pd.to_datetime(world.index)

#united_states = world.loc[world['Country_Region'] == 'US']

# Get Data:
# =============================================================================
# ny = get_state_data(world, 'New York')
# ca = get_state_data(world, 'California')
# tx = get_state_data(world, 'Texas')
# =============================================================================

# Send Email: /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/
def sendit(state):
    port = 465
    sender_email = 'parkercorya@gmail.com'
     #'lparkerjr@yahoo.com', 
    if state == 'California':
        send_to = ['dcp0426@sbcglobal.net','parkercorya@yahoo.com']
        
    elif state == "Texas":
        send_to = ['Lauersdorf.michelle89@gmail.com', 'parkercorya@yahoo.com']
        
    elif state == 'New York':
        send_to = ['sfellows@sjfc.edu', 'jessica.parker0122@gmail.com','jpreston017@gmail.com', 'parkercorya@yahoo.com']
        
    message = MIMEMultipart('alternative')
    message['Subject'] = '! Corona Virus Update !'
    message['From'] = sender_email
    message['To'] = ", ".join(send_to)
    
    text = """\
        Hello friend,
        I'm emailing you through my python script!!"""
        
    html = """\
        <html>
            <body>
                <p>Hello friend,<br>
                    Here's a link to the current global corona virus status:
                    <a href="https://www.worldometers.info/coronavirus/">Corona Virus Info</a>
                    <br>
                    <hr>
                </p>
                <img src="https://media.giphy.com/media/Lq7TFOIexfjgkCsupk/giphy.gif" alt="gif failed to be shown">
            </body>
        </html>"""
    
    # Turn these into plain/html MIMEText objects
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')
    # The email client will try to render the last part first:
    message.attach(part1)
    message.attach(part2)
    
    # DataFrame:
    get_state_data(world, state)
    
    img = open(r'C:\Users\parkd\MyScripts\raw_data\Rona{}.jpg'.format(todaystr+' '+state), 'rb')
    msg_image = MIMEImage(img.read())
    img.close()
    msg_image.add_header('Content-ID', '<image1>')
    message.attach(msg_image)    
    
    doc = open(r'C:\Users\parkd\MyScripts\Python\Notes.txt')
    password = doc.readline()
    password = password[:-1]
    doc.close()
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', port=port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, send_to, message.as_string())
        
        
sendit('New York')
sendit('Texas')
sendit('California')
        
# =============================================================================
# def send_time(time_to_send):
#     time.sleep(time_to_send.timestamp() - time.time())
#     sendit()
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
#/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\