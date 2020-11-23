import sqlite3, requests
from pushover import init, Client
from bs4 import BeautifulSoup as bs
import re

init("") #pushover api project key
IphoneUser = "" #pushover phone/computer user key
client = Client(IphoneUser)

db = sqlite3.connect('toCheck.db')
cursor = db.cursor()

def getCurrent():
    global cursor
    fetchQuery = """SELECT CheckMe.Name, CheckMe.Url, CheckMe.DesiredPrice, Websites.Name FROM CheckMe INNER JOIN Websites ON CheckMe.WebsiteID = Websites.ID"""
    results = cursor.execute(fetchQuery).fetchall()
    formattedResults = []
    for result in results:
        formatDictionary = {"Name":result[0], "Url":result[1], "DesiredPrice":result[2], "Website":result[3]}
        formattedResults.append(formatDictionary)
    return formattedResults


def CheckPrice():
    CheckList = getCurrent()
    headers = {'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36 OPR/71.0.3770.323"}
    for item in CheckList:
        html = requests.get(item['Url'], headers)
        html = bs(html.content, 'html.parser')
        if item['Website'] == "IsThereAnyDeal":
            getitadPrice(html, item)


def getitadPrice(html, item):
    url = html.find_all(class_='shopTitle--space')[0].get('href')
    html = html.find_all(class_="gh-po__price")
    html = html[1]
    html = str(html).split('>')[1].split('<')[0].split('$')[1]
    price = float(html)

    if price < float(item['DesiredPrice'].strip("$")):
        notify(item, price, url)


def notify(item, price, url):
    message = f"""{item['Name']} is now on sale for ${price}! go <a href="{url}">Here</a> to view it!"""
    client.send_message(message, title="An Item You Wished For Is On Sale", html=1, priority=1)

#CheckPrice()
#hash this line so that it isnt called when this file is imported to other projects