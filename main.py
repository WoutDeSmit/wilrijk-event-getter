import datetime
import time
# prettytable is used to display all gotten events in a nice table, this can be removed.
from prettytable import PrettyTable
from bs4 import BeautifulSoup
from selenium import webdriver
# tqdm is used for the progressbar, this can be removed, just change the for loop to "for target in targets"
from tqdm import tqdm

from calendar_adder import CalendarAdder


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
    # hide the Chrome windows that get scraped
    op = webdriver.ChromeOptions()
    op.add_argument('headless')
    # create the browser
    driver = webdriver.Chrome(options=op)
    driver.get(target["link"])
    # allow page to load
    time.sleep(1)
    # get the response and parse it
    resp = driver.page_source
    soup = BeautifulSoup(resp, 'html.parser')

    # get all the divs that contain the data for a single event
    events_div = soup.find_all("div", {
        "class": "x6s0dn4 x1lq5wgf xgqcy7u x30kzoy x9jhf4c x1olyfxc x9f619 x78zum5 x1e56ztr xyamay9 x1pi30zi x1l90r2v x1swvt13 x1gefphp"})

    # go through all the events in this div
    for i in range(len(events_div)):
        event = dict()
        event["club"] = target["club"]
        # get the name of the event from this specific span
        name = events_div[i].find_all("span", {
            "html-span xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x1hl2dhg x16tdsg8 x1vvkbs"})
        name = name[0].text.strip()
        event['name'] = name
        # get the date of the event from this specific span
        date = events_div[i].find_all("span", {"class": "x1lliihq x6ikm8r x10wlt62 x1n2onr6 xlyipyv xuxw1ft x1j85h84"})
        date = date[0].text.strip()
        # get the link of the event from this specific span
        link = events_div[i].find_all("a", {"class": "x1i10hfl x1qjc9v5 xjbqb8w xjqpnuy xa49m3k xqeqjp1 x2hbi6w x13fuv20 xu3j5b3 x1q0q8m5 x26u7qi x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1ypdohk xdl72j9 x2lah0s xe8uvvx xdj266r xat24cr x1mh8g0r x2lwn1j xeuugli xexx8yu x4uap5 x18d9i69 xkhd6sd x1n2onr6 x16tdsg8 x1hl2dhg xggy1nq x1ja2u2z x1t137rt x1o1ewxj x3x9cwd x1e5q0jg x13rtm0m x1q0g3np x87ps6o x1lku1pv x1rg5ohu x1a2a7pz xwzfr38 xktsk01 xb172dh"}, href=True)
        link = link[0]['href'].strip()
        event['link'] = link

        # the date can be structured in a couple of ways, we go through each option and handle it separately
        if date == "Nu bezig":
            date = str(datetime.datetime.now())
            date = date[0:19]
            date = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
            event['is_happening'] = True
        elif "-" in date:
            date_cut = date[4:16]
            date_cut = date_cut.replace("mrt", "mar").replace("mei", "may").replace("okt", "oct").strip()
            date_formatted = datetime.datetime.strptime(date_cut, '%d %b. %Y')
            date = date_formatted
            event['is_happening'] = False
        elif date[11:16].strip().isdigit():
            date_cut = date[4:25].strip()
            date_cut = date_cut.replace("mrt", "mar").replace("mei", "may").replace("okt", "oct").strip()
            date_formatted = datetime.datetime.strptime(date_cut, '%d %b. %Y om %H:%M')
            date = date_formatted
            event['is_happening'] = False
        else:
            date_cut = date[4:20].strip() + ":" + str(datetime.datetime.now().year)
            date_cut = date_cut.replace("mrt", "mar").replace("mei", "may").replace("okt", "oct").strip()
            date_formatted = datetime.datetime.strptime(date_cut, '%d %b. om %H:%M:%Y')
            date = date_formatted
            event['is_happening'] = False
        event['date'] = date
        event_list.append(event)

    driver.close()

# events can be hosted by multiple clubs, so we check for duplicates
unique_event_list = []
for event in event_list:
    if {"name": event["name"], "date": event["date"], 'is_happening': event['is_happening'], 'link': event['link']} not in unique_event_list:
        unique_event_list.append({"name": event["name"], "date": event["date"], 'is_happening': event['is_happening'], 'link': event['link']})

# duplicated events get added once but each club that hosts it gets added in a clubs list
event_list_condensed = []
for unique_event in unique_event_list:
    club_list = []
    for event in event_list:
        if event['name'] == unique_event["name"]:
            club_list.append(event["club"])
    event_list_condensed.append({"club": club_list, "name": unique_event["name"], "date": unique_event["date"], 'is_happening': unique_event['is_happening'], 'link': unique_event['link']})
event_list_condensed = sorted(event_list_condensed, key=lambda d: d['date'])

# a nice table gets made to display all the events, this can be deleted to
# Specify the Column Names while initializing the Table
myTable = PrettyTable(["Clubs", "Event naam", "Datum"])

# check which events are already in the calendar, so they don't get added multiple times
calendar_service = CalendarAdder()
events_in_calendar = calendar_service.get_events()
summary_in_calendar = []
for event in events_in_calendar:
    summary_in_calendar.append(event['summary'])

# Add rows and add events to calendar
for event in event_list_condensed:
    myTable.add_row([event["club"], event["name"], event["date"]])

    # events that are currently happening get excluded as the time is incorrect
    if not event['is_happening'] and event['name'] not in summary_in_calendar:
        club_str = ""
        for club in event["club"]:
            club_str += club + ", "
        club_str = club_str[:-2]
        description = f"{event['name']} van {club_str}. \nLink: {event['link']}"
        calendar_service.create_event(event['date'], event['date'] + datetime.timedelta(hours=5), event['name'], description)

print(myTable)
