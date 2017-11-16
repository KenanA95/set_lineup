import json
import time
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import tkinter as tk
from selenium.common.exceptions import TimeoutException


__doc__ = """
TODO:
    - Check if the 'start players' button was successfully selected for each date
    - Use explicit waits when loading the roster pages
    - Better login validation
    - Use modern theme/style
    - Place asserts throughout selenium gets
    - Replace update_idletasks
"""


class LoginWindow:
    def __init__(self, master, driver):
        self.master = master
        self.driver = driver
        self.master.title("Login to Yahoo Fantasy Sports")
        self.master.geometry("300x100")
        self.login_url = "https://login.yahoo.com/config/login?.src=fantasy&specId=usernameRegWithName&.intl=" \
                         "us&.lang=en-US&.done=https://basketball.fantasysports.yahoo.com/"
        self.team_url = None

        # Initialize entry fields
        self.username_label = tk.Label(self.master, text="Username")
        self.password_label = tk.Label(self.master, text="Password")
        self.username = tk.Entry(self.master)
        self.password = tk.Entry(self.master, show="*")
        self.login_btn = tk.Button(self.master, text='Login', command=self.login)
        self.login_info = tk.Label(self.master, text="")

        # Setup Layout
        self.username_label.grid(row=0)
        self.password_label.grid(row=1)
        self.username.grid(row=0, column=1)
        self.password.grid(row=1, column=1)
        self.login_btn.grid(columnspan=2)
        self.login_info.grid(row=3)

        # Bind enter button to login
        master.bind('<Return>', self.login)

    def login(self, event=None):
        # Grab the entry fields and let the user know the process has started
        username = self.username.get()
        password = self.password.get()
        self.login_info.config(text="Logging in...")
        self.login_info.update_idletasks()

        # Navigate to the login URL
        self.driver.get(self.login_url)
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "login-username")))

        # Put my email in and hit next
        self.driver.find_element_by_id("login-username").send_keys(username)
        self.driver.find_element_by_id("login-signin").click()

        # If the page does not proceed immediately its an invalid username
        try:
            WebDriverWait(self.driver, 2).until(EC.presence_of_element_located((By.ID, "login-passwd")))
        except TimeoutException:
            self.login_info.config(text="Invalid username",  fg="red")
            return

        # Put my password in and login
        self.driver.find_element_by_id("login-passwd").send_keys(password)
        self.driver.find_element_by_id("login-signin").click()

        # If the page does not proceed immediately its an invalid password
        try:
            WebDriverWait(self.driver, 2).until(EC.presence_of_element_located((By.LINK_TEXT, "My Team")))
        except TimeoutException:
            self.login_info.config(text="Invalid password", fg="red")
            return

        self.team_url = self.driver.find_element_by_link_text("My Team").get_attribute('href')
        self.master.destroy()


class MainWindow:
    def __init__(self, master, driver, team_url):
        self.master = master
        self.driver = driver
        self.team_url = team_url
        self.master.geometry("500x500")
        self.master.title("Yahoo Fantasy Lineup")
        # Navigate to the users team
        self.driver.get(self.team_url)

        # Initialize fields
        self.days_label = tk.Label(master, text="Select Number of Days to Start Players")
        self.days = tk.StringVar(master)
        self.days.set(30)
        self.n_days = tk.OptionMenu(master, self.days, *range(100))
        self.log_label = tk.Label(master, text="Output Log")
        scrollbar = tk.Scrollbar(master, orient=tk.VERTICAL)
        self.log = tk.Listbox(master, width=50, height=50, yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.log.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.submit = tk.Button(master, text='Submit', command=self.start_players)

        # Setup Layout
        self.days_label.pack()
        self.n_days.pack()
        self.submit.pack()
        self.log_label.pack()
        self.log.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

    def start_players(self):
        self.log_label.configure(text="Output Log - Running")
        self.log_label.update_idletasks()

        # Get the number of days the user selected
        n_days = int(self.days.get())

        # Generate string representations of the next n days
        now = datetime.datetime.now()
        today = datetime.date(now.year, now.month, now.day)
        dates = [today + datetime.timedelta(days=i) for i in range(n_days)]

        # Clear the current log
        self.log.delete(0, tk.END)
        self.log.update_idletasks()

        for date in dates:
            roster = self.team_url + "/team?&date={0}".format(date)
            self.driver.get(roster)
            # TODO: Use explicit wait
            time.sleep(2)
            # TODO: Check if the operation was successful
            self.driver.find_element_by_link_text("Start Active Players").click()
            time.sleep(2)
            self.log.insert(tk.END, "Roster successfully set for: {0}".format(date))
            self.log.update_idletasks()

        self.log_label.configure(text="Output Log")

if __name__ == "__main__":

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    caps = DesiredCapabilities().CHROME
    caps['pageLoadStrategy'] = "none"
    driver = webdriver.Chrome(desired_capabilities=caps, chrome_options=chrome_options)
    driver.set_window_size(1920, 1080)

    root = tk.Tk()
    login = LoginWindow(root, driver)
    root.mainloop()

    root = tk.Tk()
    main = MainWindow(root, driver, team_url="https://basketball.fantasysports.yahoo.com/nba/71943/2")
    root.mainloop()

    driver.close()
