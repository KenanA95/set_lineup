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
import tkinter as tk


class LoginFrame:
    def __init__(self, master, driver):
        self.master = master
        self.driver = driver

        master.title("Login to Yahoo Fantasy Sports")

        # Initialize entry fields
        self.username_label = tk.Label(master, text="Username")
        self.password_label = tk.Label(master, text="Password")
        self.username = tk.Entry(master)
        self.password = tk.Entry(master, show="*")
        self.login_btn = tk.Button(master, text='Login', command=self.login)

        # Setup Layout
        self.username_label.grid(row=0, sticky='E')
        self.password_label.grid(row=1, sticky='E')
        self.username.grid(row=0, column=1)
        self.password.grid(row=1, column=1)
        self.login_btn.grid(columnspan=2)

        # Hit login button if user hits enter
        root.bind('<Return>', self.login)

    def login(self, event=None):

        username = self.username.get()
        password = self.password.get()

        login_url = "https://login.yahoo.com/config/login?.src=fantasy&specId=usernameRegWithName&." \
                    "intl=us&.lang=en-US&.done=https://basketball.fantasysports.yahoo.com/"

        self.driver.get(login_url)

        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "login-username")))

        # Put my email in and hit next
        self.driver.find_element_by_id("login-username").send_keys(username)
        self.driver.find_element_by_id("login-signin").click()

        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "login-passwd")))

        # Put my password in and login
        self.driver.find_element_by_id("login-passwd").send_keys(password)
        self.driver.find_element_by_id("login-signin").click()

        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.LINK_TEXT, "My Team")))
        team_url = self.driver.find_element_by_link_text("My Team").get_attribute('href')

        return team_url


# days => number of days to set your lineup starting from today's date
def start_active_players(driver, team_url, days):

    # Go to my team's roster
    driver.get(team_url)

    # Set the roster for n days
    now = datetime.datetime.now()
    today = datetime.date(now.year, now.month, now.day)
    dates = [today + datetime.timedelta(days=i) for i in range(days)]

    for date in dates:
        roster = team_url + "/team?&date={0}".format(date)
        driver.get(roster)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.LINK_TEXT, "Start Active Players")))
        driver.find_element_by_link_text("Start Active Players").click()
        print("Roster successfully set for: {0}".format(date))


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

    driver = webdriver.Chrome()
    root = tk.Tk()
    gui = LoginFrame(root, driver)
    root.mainloop()
