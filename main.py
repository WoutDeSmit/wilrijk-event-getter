import datetime
import time
from prettytable import PrettyTable
from bs4 import BeautifulSoup
from selenium import webdriver
from tqdm import tqdm

from calendar_adder import create_event, get_events

# https://googlechromelabs.github.io/chrome-for-testing/
targets = [{"link": "https://www.facebook.com/INGENIUM.FTI/events", "club": "Ingenium"},
           {"link": "https://www.facebook.com/Fabiantisgroot/events", "club": "Fabiant"},
           {"link": "https://www.facebook.com/Campinaria/events", "club": "Campinaria"},
           {"link": "https://www.facebook.com/DIEFKAntwerpen/events", "club": "DIEFKA"},
           {"link": "https://www.facebook.com/WINAKantwerpen/events", "club": "WINAK"},
           {"link": "https://www.facebook.com/UFKAntwerpen/events", "club": "UFKA"},
           {"link": "https://www.facebook.com/DemetrisUA/events", "club": "Demetris"},
           {"link": "https://www.facebook.com/KringDerAlchemisten/events", "club": "KDA"},
           {"link": "https://www.facebook.com/BiomedicaAntwerpen/events", "club": "Biomedica"},
           {"link": "https://www.facebook.com/aesculapia/events", "club": "Aesculapia"},
           {"link": "https://www.facebook.com/HeraUAntwerpen/events", "club": "Hera"}]

event_list = []
for target in tqdm(targets):
    op = webdriver.ChromeOptions()
    op.add_argument('headless')
    driver = webdriver.Chrome(options=op)
    driver.get(target["link"])
    time.sleep(1)
    resp = driver.page_source
    soup = BeautifulSoup(resp, 'html.parser')

    events_div = soup.find_all("div", {
        "class": "x6s0dn4 x1lq5wgf xgqcy7u x30kzoy x9jhf4c x1olyfxc x9f619 x78zum5 x1e56ztr xyamay9 x1pi30zi x1l90r2v x1swvt13 x1gefphp"})

    for i in range(len(events_div)):
        event = dict()
        event["club"] = target["club"]
        name = events_div[i].find_all("span", {
            "html-span xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x1hl2dhg x16tdsg8 x1vvkbs"})
        name = name[0].text.strip()
        event['name'] = name
        date = events_div[i].find_all("span", {"class": "x1lliihq x6ikm8r x10wlt62 x1n2onr6 xlyipyv xuxw1ft x1j85h84"})
        date = date[0].text.strip()
        if date == "Nu bezig":
            date = str(datetime.datetime.now())
            date = date[0:19]
            date = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
            event['is_today'] = True
        elif "-" in date:
            date_cut = date[4:16]
            date_cut = date_cut.replace("mrt", "mar").replace("mei", "may").replace("okt", "oct").strip()
            date_formatted = datetime.datetime.strptime(date_cut, '%d %b. %Y')
            date = date_formatted
            event['is_today'] = False
        elif date[11:16].strip().isdigit():
            date_cut = date[4:25].strip()
            date_cut = date_cut.replace("mrt", "mar").replace("mei", "may").replace("okt", "oct").strip()
            date_formatted = datetime.datetime.strptime(date_cut, '%d %b. %Y om %H:%M')
            date = date_formatted
            event['is_today'] = False
        else:
            date_cut = date[4:20].strip() + ":" + str(datetime.datetime.now().year)
            date_cut = date_cut.replace("mrt", "mar").replace("mei", "may").replace("okt", "oct").strip()
            date_formatted = datetime.datetime.strptime(date_cut, '%d %b. om %H:%M:%Y')
            date = date_formatted
            event['is_today'] = False
        event['date'] = date
        event_list.append(event)

    driver.close()

name_list = []
for event in event_list:
    if {"name": event["name"], "date": event["date"], 'is_today': event['is_today']} not in name_list:
        name_list.append({"name": event["name"], "date": event["date"], 'is_today': event['is_today']})

event_list_condensed = []
for name in name_list:
    club_list = []
    for event in event_list:
        if event['name'] == name["name"]:
            club_list.append(event["club"])
    event_list_condensed.append({"club": club_list, "name": name["name"], "date": name["date"], 'is_today': name['is_today']})
event_list_condensed = sorted(event_list_condensed, key=lambda d: d['date'])

# Specify the Column Names while initializing the Table
myTable = PrettyTable(["Clubs", "Event naam", "Datum"])

events_in_calendar = get_events()
summary_in_calendar = []
for event in events_in_calendar:
    summary_in_calendar.append(event['summary'])

# Add rows and add events to calendar
for event in event_list_condensed:
    myTable.add_row([event["club"], event["name"], event["date"]])

    if not event['is_today'] and event['name'] not in summary_in_calendar:
        club_str = ""
        for club in event["club"]:
            club_str += club + ", "
        club_str = club_str[:-2]
        description = f"{event['name']} van {club_str}"
        create_event(event['date'], event['date'] + datetime.timedelta(hours=5), event['name'], description)

print(myTable)
