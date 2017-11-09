import json
import time
import datetime
import smtplib
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


# Login into Yahoo fantasy sports and figure out the league id and team
def login(driver, username, password):
    login_url = "https://login.yahoo.com/config/login?.src=fantasy&specId=usernameRegWithName&." \
                "intl=us&.lang=en-US&.done=https://basketball.fantasysports.yahoo.com/"

    driver.get(login_url)

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "login-username")))

    # Put my email in and hit next
    driver.find_element_by_id("login-username").send_keys(username)
    driver.find_element_by_id("login-signin").click()

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "login-passwd")))

    # Put my password in and login
    driver.find_element_by_id("login-passwd").send_keys(password)
    driver.find_element_by_id("login-signin").click()

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.LINK_TEXT, "My Team")))
    driver.find_element_by_link_text("My Team").click()
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.LINK_TEXT, "Start Active Players")))

    # Parse the url to find the league and team ids. League ids are always 5 digits
    start_index = driver.current_url.find("nba/") + 4
    ids = driver.current_url[start_index:]
    league_id, team_id = ids[:5], ids[6:]

    return league_id, team_id


# days => number of days to set your lineup starting from today's date
def start_active_players(driver, days):

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.LINK_TEXT, "My Team")))
    time.sleep(3)
    # Click 'My Team' button
    driver.find_element_by_link_text("My Team").click()
    team_url = driver.current_url + "/team?&date="

    # Set the roster for n days
    now = datetime.datetime.now()
    today = datetime.date(now.year, now.month, now.day)
    dates = [today + datetime.timedelta(days=i) for i in range(days)]

    for date in dates:

        roster = team_url + str(date)
        driver.get(roster)
        time.sleep(10)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.LINK_TEXT, "Start Active Players")))
        driver.find_element_by_link_text("Start Active Players").click()


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

    # Open a headless browser and don't wait for JS heavy pages to fully load
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    caps = DesiredCapabilities().CHROME
    caps['pageLoadStrategy'] = "none"
    driver = webdriver.Chrome(desired_capabilities=caps, chrome_options=chrome_options)
    driver.set_window_size(1920, 1080)
    driver.maximize_window()

    # Grab my info for logins
    with open('D:/repos/set_lineup/credentials.json') as json_data:
        login_info = json.load(json_data)
        yahoo = login_info['yahoo']
        gmail = login_info['gmail']

    # Handle any unforeseen errors
    league_id, user_id = login(driver, yahoo['user'], yahoo['password'])
    driver.close()
