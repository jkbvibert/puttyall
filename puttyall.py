import os

from pywinauto import Application, keyboard, clipboard
import time
import configparser
import requests
from requests.auth import HTTPBasicAuth
import getpass
import re
from colorama import init, Fore, Back, Style
from tkinter import Tk

init()
config = configparser.ConfigParser()
config.read('params.txt')


if config.has_option('JCA', 'email'):  #login to API and check if API is functioning as expected
    email = config.get('JCA', 'email')
else:
    config['JCA'] = {'email': ''}
    email = input("Enter your JCA email address: ")
    match = re.search(r"(.+)[@](\S+)(\.com)", email)
    if not match:
        print(Style.BRIGHT + Fore.RED + "Not a valid email" + Style.RESET_ALL)
        exit(1)
    config['JCA']['email'] = email

jcapw = getpass.getpass('JCA Password: ')

resp = requests.get('https://<scrubbed>/admin/api/cloud/v1/users/current', auth=HTTPBasicAuth(email, jcapw))
if resp.status_code != 200:
    print("Received non-200 status code [%s] (likely incorrect pw)\nABORTING!" % resp.status_code)
    exit(1)
else:
    resp_formatted = resp.json()
    if resp_formatted['id'] == 0:
        print("ID == 0\nABORTING!")
        exit(1)

jcaid = input("Enter the InstallationID to open: ")

# grab hosts for that JCA id
resp = requests.get('https://<scrubbed>/admin/api/cloud/v1/vm/installation/' + jcaid, auth=HTTPBasicAuth(email, jcapw))
containers = resp.json()
servers = []
for each in containers:
    servers.append(each['hostname'])
servers = list(set(servers))
servers.sort(reverse=True)
if config.has_option('SSH', 'username'):
    sshun = config.get('SSH', 'username')
else:
    config['SSH'] = {'username': ''}
    sshun = input("Enter your SSH username: ")
    config['SSH']['username'] = sshun
#sshpw = getpass.getpass('SSH passphrase: ')
with open('params.txt', 'w') as configfile:
    config.write(configfile)

windows = []
cmd_pmpt = Application(backend="uia").connect(title_re="(Command Prompt.*)")
cmd_pmpt = cmd_pmpt.top_window()
for each in servers:
    app = Application().start(r"C:\Program Files (x86)\PuTTY\putty.exe -ssh jvibert@%s" % each)
    pt = app.PuTTY
    pt_sec_alert = app.PuTTYSecurityAlert
    pt.wait('ready')
    time.sleep(2) #adjust if time between servers is too slow
    if pt_sec_alert.exists():
        pt_sec_alert.Yes.click()
    windows.append(pt)
cmd_pmpt.set_focus()

# def repaint():  #functionality to make the windows fit to your screen size, and also repaint upon win
#     # 1920x1200 window size
#     win_height = 1200
#     x_pos = 0
#     y_pos = 0
#     # if 3 or less windows do the below
#     if len(windows) <= 3:
#         win_width = round(1920 / len(windows))
#         for window in windows:
#             window.move_window(x=x_pos, y=y_pos, width=win_width, height=win_height, repaint=True)
#             x_pos = x_pos + win_width
#     elif len(windows) == 4:
#         win_width = round(1920 / 2)
#         win_height = round(1200 / 2)
#         for i in range(len(windows)):
#             if i < 2:
#                 windows[i].move_window(x=x_pos, y=y_pos, width=win_width, height=win_height, repaint=True)
#                 x_pos = x_pos + win_width
#             else:
#                 if i == 2:
#                     x_pos = 0
#                     y_pos = win_height - 10
#                 windows[i].move_window(x=x_pos, y=y_pos, width=win_width, height=win_height, repaint=True)
#                 x_pos = x_pos + win_width
#     elif len(windows) > 4 and len(windows) <= 6:  # if between > 3 and <= 6 then do two lines
#         win_width = round(1920 / round(len(windows) / 2))
#         win_height = round(win_height / 2)
#         for i in range(len(windows)):
#             if i <= 2:
#                 if len(windows) == 5:
#                     win_width = round(1920 / 3)
#                 windows[i].move_window(x=x_pos - 5, y=y_pos, width=win_width + 10, height=win_height, repaint=True)
#                 x_pos = x_pos + win_width
#             else:
#                 if i == 3 and (len(windows) == 5 or len(windows) == 6):
#                     x_pos = 0
#                     win_width = round(1920 / (len(windows) - i))
#                 y_pos = win_height
#                 if i == 5:
#                     windows[i].move_window(x=x_pos - 5, y=y_pos - 5, width=win_width + 5, height=win_height - 20, repaint=True)
#                 else:
#                     windows[i].move_window(x=x_pos - 5, y=y_pos - 5, width=win_width + 5, height=win_height - 20, repaint=True)
#                 x_pos = x_pos + win_width
#     elif len(windows) > 6 and len(windows) <= 9:  # if between > 6 and <= 9 then do three lines
#         win_width = round(1920 / round(len(windows) / 3))
#         win_height = round(1200 / 3)
#         y_pos_2 = round(1200 / 3)
#         y_pos_3 = (y_pos_2 * 2)
#
#         #8 = <scrubbed internal URL>
#         for i in range(len(windows)):
#             if i <= 2:
#                 windows[i].move_window(x=x_pos - 5, y=y_pos, width=win_width + 5, height=win_height + 5, repaint=True)
#             elif i > 2 and i <= 5:
#                 if i == 3:
#                     x_pos = 0
#                 windows[i].move_window(x=x_pos - 5, y=y_pos_2, width=win_width + 5, height=win_height + 5, repaint=True)
#             else:
#                 if i == 6:
#                     x_pos = 0
#                 if len(windows) == 8:
#                     win_width = round(1920 / 2)
#                     windows[i].move_window(x=x_pos - 5, y=y_pos_3, width=win_width + 5, height=win_height - 30, repaint=True)
#                 else:
#                     windows[i].move_window(x=x_pos - 5, y=y_pos_3, width=win_width + 5, height=win_height, repaint=True)
#             x_pos = x_pos + win_width
#     else:  #<scrubbed customer names> for testing
#         win_width = round(1920 / round(len(windows) / 3))
#         win_height = round(1200 / 3)
#         y_pos_2 = round(1200 / 3)
#         y_pos_3 = (y_pos_2 * 2)
#
#         for i in range(len(windows)):
#             if i < round(len(windows) * .33):
#                 windows[i].move_window(x=x_pos - 6, y=y_pos, width=win_width + 5, height=win_height + 5, repaint=True)
#             elif i >= round(len(windows) * .33) and i < round(len(windows) * .66) - 1:
#                 if i == (round(len(windows) * .33)):
#                     x_pos = 0
#                 windows[i].move_window(x=x_pos - 6, y=y_pos_2, width=win_width + 5, height=win_height + 5, repaint=True)
#             else:
#                 if i == round((len(windows) / 3) * 2) - 1:
#                     x_pos = 0
#                     win_width = round(1920 / (len(windows) - i))
#                 windows[i].move_window(x=x_pos - 6, y=y_pos_3, width=win_width + 5, height=win_height - 25,
#                                        repaint=True)
#             x_pos = x_pos + win_width
#     cmd_pmpt.set_focus()

# repaint()

def run_cmd(curr_win, cmd_to_run):
    curr_win.set_focus()
    keyboard.send_keys(cmd_to_run + '{ENTER}', with_spaces=True)


r = Tk()
while True:
    cmd = input("Enter command to send to all windows: ")
    cnt = 0
    for window in windows: #Can't handle removing more than one window at a time
        if window.exists() == False:
            windows.remove(window)
            cnt += 1
    # while cnt != 0:
    #     repaint()
    #     cnt = 0
    if cmd.lower() == 'exit':
        for window in windows:
            window.set_focus()
            keyboard.send_keys('{VK_CONTROL down}{c down}{VK_CONTROL up}{c up}exit{ENTER}')
        exit(0)
    else:
        r.clipboard_append(cmd)
        for window in windows:
            window.set_focus()
            keyboard.send_keys('+{INS}' + '{ENTER}', with_spaces=True)
        r.clipboard_clear()
        cmd_pmpt.set_focus()

r.destroy()
#https://stackoverflow.com/questions/49953231/putty-via-pywinauto?rq=1
#https://pywinauto.readthedocs.io/en/latest/code/pywinauto.keyboard.html
#https://github.com/pywinauto/pywinauto/issues/533