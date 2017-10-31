from selenium import webdriver
import json
import time

# Grab my login info
with open('credentials.json') as json_data:
    yahoo = json.load(json_data)

login_url = "https://login.yahoo.com/config/login?.src=fantasy&specId=usernameRegWithName&." \
             "intl=us&.lang=en-US&.done=https://basketball.fantasysports.yahoo.com/"

driver = webdriver.Chrome()
driver.get(login_url)

# Put my email in and hit next
driver.find_element_by_id("login-username").send_keys(yahoo['user'])
driver.find_element_by_id("login-signin").click()

# Give it a second to complete the redirect
time.sleep(1)

# Put my password in and login
driver.find_element_by_id("login-passwd").send_keys(yahoo['password'])
driver.find_element_by_id("login-signin").click()

# Start active players for today's date
date = time.strftime("%Y-%m-%d")
todays_roster = "https://basketball.fantasysports.yahoo.com/nba/71943/2?date={0}".format(date)
driver.get(todays_roster)
driver.find_element_by_link_text("Start Active Players").click()
driver.close()
