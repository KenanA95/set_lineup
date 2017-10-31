from selenium import webdriver
import json
import time
import datetime


def login(username, password):
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


# n => number of days to set your lineup starting from today's date
def start_active_players(n):
    now = datetime.datetime.now()
    today = datetime.date(now.year, now.month, now.day)
    days = [today + datetime.timedelta(days=i) for i in range(n)]

    for day in days:
        roster = "https://basketball.fantasysports.yahoo.com/nba/71943/2?date={0}".format(day)
        driver.get(roster)
        driver.find_element_by_link_text("Start Active Players").click()
        time.sleep(1)


if __name__ == "__main__":

    # Pop open the browser
    driver = webdriver.Chrome()

    # Grab my info and login
    with open('credentials.json') as json_data:
        yahoo = json.load(json_data)

    login(yahoo['user'], yahoo['password'])

    #  Start active players for the entire week
    start_active_players(n=7)

    driver.close()
