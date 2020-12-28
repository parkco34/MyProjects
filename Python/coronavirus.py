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
from selenium.webdriver.common.action_chains import ActionChains

def duplicated_varnames(df):
    """Return a dict of all variable names that
    are duplicated in a given dataframe."""
    repeat_dict = {}
    var_list = list(df) # list of varnames as strings
    for varname in var_list:
        # make a list of all instances of that varname
        test_list = [v for v in var_list if v == varname]
        # if more than one instance, report duplications in repeat_dict
        if len(test_list) > 1:
            repeat_dict[varname] = len(test_list)
    return repeat_dict

# Pycharm keyboard help: /\/\/\/\/\/\/\/\/\/\//\/\/\/\/\/\/\/\/\/\//\/\/\/\/\/\/\/\/\/\//\/\/\/\/\/\/\/
# run code: alt+shift+e
# Commenting: ctrl + /
# /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\
final_date = '07-22-2020'
#start_date = '01-22-2020'
start_date = '04-22-2020'
today = date.today()
todaystr = today.strftime('%m-%d-%Y')
yesterday = today - timedelta(days=1)
yesterday = yesterday.strftime('%m-%d-%Y')


def get_dates(start_date):
    date_i = datetime.strptime(start_date, '%m-%d-%Y')
    # dates = pd.date_range(date_i, today - timedelta(days=1), freq='d')
    # dates = pd.date_range(start_date, yesterday, freq='d')
    # Earlier Dates
    dates = pd.date_range(start_date, final_date, freq='d')
    dates = dates.strftime('%m-%d-%Y')
    dates = dates.tolist()
    return dates


def replace_columns(df, updated_cols):
    k = 0
    for i in df.columns:
        for j in updated_cols:
            seq = difflib.SequenceMatcher(None, i, j).ratio() * 100
            if (seq >= 54) & (i != j):
                newcol = re.sub(i, j, i)
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

    _ = data.plot(figsize=(15, 5), subplots=False, title=state + ' ' + 'Rona')
    _ = plt.xlabel('Date')
    _ = plt.ylabel('Infected')
    plt.savefig('/home/parker/python/corona_initial.csv'.format(todaystr + ' ' + state))
    return data


# I need a function that will do this for me: If a column is added to raw data I'm scraping,
# add the new column and branch off to create new data frame and continue concatenating data
ff_driver = r"C:\Users\cparker\Desktop\PYTHON\geckodriver.exe"
site = "https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_daily_reports"
options = FirefoxOptions()
options.add_argument("--start-maximized")
options.headless = True
assert options.headless


def get_new_columns(end_date):
    driver = webdriver.Firefox(executable_path=ff_driver, options=options)
    time.sleep(.8)
    driver.get(site)
    time.sleep(.5)

    # Ignore irrelevant exceptions
    ignored_exceptions = (NoSuchElementException, StaleElementReferenceException)
    waiting = WebDriverWait(driver, 10, ignored_exceptions=ignored_exceptions)

    # Locate nodes in XML doc
    waiting.until(EC.element_to_be_clickable((By.XPATH, '//*[@title="{}.csv"]'.format(end_date)))).click()
    waiting.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="raw-url"]'))).click()

    time.sleep(.8)
    # Store raw data in variable
    raw = waiting.until(EC.element_to_be_clickable((By.XPATH, '/html/body/pre'))).text
    raw_data = StringIO(raw)
    dataframe = pd.read_csv(raw_data)

    return list(dataframe.columns)


def consolidate_columns(new_dframe, old_dframe):
    # Getting both dataframe columns as lists and extracting the missing columns and their indices
    oldcol_list = list(old_dframe.columns)
    newcol_list = list(new_dframe.columns)
    # Difference between lists or arrays, where assume_unique=True prevents the function from sorting the values
    missing_list = np.setdiff1d(newcol_list, oldcol_list, assume_unique=True).tolist()

    for i in missing_list:
        # Gets index of the missing column names
        j = new_dframe.columns.get_loc(i)
        old_dframe.insert(j, i, "")


def scrape(path_to_click):
    # Get latest columns
    new_columns = get_new_columns(final_date)

    driver = webdriver.Firefox(executable_path=ff_driver, options=options)
    driver.get(site)

    ignored_exceptions = (NoSuchElementException, StaleElementReferenceException)
    waiting = WebDriverWait(driver, 10, ignored_exceptions=ignored_exceptions)

    df = pd.DataFrame([], columns=new_columns)

    for dt in get_dates(start_date):
        print(dt)
        try:
            waiting.until(EC.element_to_be_clickable((By.XPATH, '//*[@title="{}.csv"]'.format(dt)))).click()
            time.sleep(1.5)
            # Makes the element that is not visible, visible so it can click where it needs to
            ActionChains(driver).move_to_element(driver.find_element(By.XPATH, path_to_click)).click(driver.find_element(By.XPATH, path_to_click))
            waiting.until(EC.element_to_be_clickable((By.XPATH, path_to_click))).click()
        except TimeoutException as ex:
            print("xpath: Something is going wrong at {}:".format(dt) + str(ex))

        time.sleep(.5)
        raw = waiting.until(EC.element_to_be_clickable((By.XPATH, '/html/body/pre'))).text
        raw_data = StringIO(raw)

        if dt != start_date:
            df2 = pd.read_csv(raw_data, names=new_columns)
            replace_columns(df2, new_columns)
            dup_dict = duplicated_varnames(df2)
            print(dup_dict)
            df2['Last_Update'] = pd.to_datetime(df2['Last_Update'])
            df = pd.concat([df, df2], axis=0, ignore_index=True)

        else:
            df1 = pd.read_csv(raw_data, names=new_columns)
            replace_columns(df1, new_columns)
            df1['Last_Update'] = pd.to_datetime(df1['Last_Update'])
            df = pd.concat([df, df1], axis=0, ignore_index=True)

        time.sleep(.5)
        # print(dt)
        driver.back()
        time.sleep(.5)
        driver.back()
        time.sleep(.5)

    return df


rona = scrape('//*[@id="raw-url"]')

# Set datetime index:
rona['Last_Update'] = pd.to_datetime(rona['Last_Update']).dt.date
rona = rona.set_index('Last_Update')

# Get old dataframe
df_i = pd.read_csv(r'C:\Users\cparker\Desktop\PYTHON\rona04-22-2020.csv', low_memory=False)
# Update the columns for our new data
consolidate_columns(rona, df_i)

# }}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}
rona.to_csv(r'C:\Users\cparker\Desktop\PYTHON\rona{}.csv'.format(final_date))
# }}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}

world = pd.concat([df_i, rona], axis=0, ignore_index=True)
world['Last_Update'] = pd.to_datetime(world['Last_Update'])  # .dt.date
world = world.set_index('Last_Update')
world.index = pd.to_datetime(world.index)
united_states = world.loc[world['Country_Region'] == 'US']

united_states = rona.loc[rona['Country_Region'] == 'US']

# Get Data:
# =============================================================================
ny = get_state_data(rona, 'New York')
ca = get_state_data(rona, 'California')
tx = get_state_data(rona, 'Texas')
az = get_state_data(rona, 'Arizona')
wash = get_state_data(rona, 'Washington')
# =============================================================================
# Send Email: /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\
# def send_it(state):
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
# =============================================================================
# =============================================================================
#     file =
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
