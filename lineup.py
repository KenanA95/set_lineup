import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import json
import time
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


# Login into Yahoo fantasy sports
def login(driver, username, password):
    login_url = "https://login.yahoo.com/config/login?.src=fantasy&specId=usernameRegWithName&." \
                "intl=us&.lang=en-US&.done=https://basketball.fantasysports.yahoo.com/"

    driver.get(login_url)

    # Put my email in and hit next
    driver.find_element_by_id("login-username").send_keys(username)
    driver.find_element_by_id("login-signin").click()

    # Give it a second to complete the redirect
    time.sleep(1)

    # Put my password in and login
    driver.find_element_by_id("login-passwd").send_keys(password)
    driver.find_element_by_id("login-signin").click()


# days => number of days to set your lineup starting from today's date
def start_active_players(driver, days):
    now = datetime.datetime.now()
    today = datetime.date(now.year, now.month, now.day)
    dates = [today + datetime.timedelta(days=i) for i in range(days)]

    for date in dates:
        roster = "https://basketball.fantasysports.yahoo.com/nba/71943/2?date={0}".format(date)
        driver.get(roster)
        driver.find_element_by_link_text("Start Active Players").click()
        time.sleep(1)


# Email notification to confirm my lineup has been set
def send_email(username, password, subject, recipient, text):

    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['To'] = recipient
    msg.attach(MIMEText(text, 'plain'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(username, password)
    server.sendmail(username, recipient, msg.as_string())
    server.quit()


if __name__ == "__main__":

    # Open a headless browser
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(chrome_options=chrome_options)
    driver.set_window_size(1920, 1080)
    driver.maximize_window()

    # Grab my info for logins
    with open('credentials.json') as json_data:
        login_info = json.load(json_data)
        yahoo = login_info['yahoo']
        gmail = login_info['gmail']

    # Handle any unforeseen errors
    try:
        login(driver, yahoo['user'], yahoo['password'])
        start_active_players(driver, days=7)
    except Exception as e:
        err_msg = "Exception type: {0} \n" \
                  "Error message: {1}".format(type(e), e)
        send_email(gmail['user'], gmail['password'], "Error Setting Lineup", "kenan.r.alkiek@gmail.com", err_msg)
        driver.close()
        sys.exit(-1)

    text = "Your lineup has been set for the next {0} days".format(7)
    send_email(gmail['user'], gmail['password'], "Lineup Set", "kenan.r.alkiek@gmail.com", text)
    driver.close()
