import PySimpleGUI as gui
import sqlite3 as sql
import autoCheck, requests
from bs4 import BeautifulSoup as bs

headers = {'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36 OPR/71.0.3770.323"}

db = sql.connect(r'toCheck.db')
cursor = db.cursor()
windowsLoaded = 1
gui.change_look_and_feel("darkAmber")


def getAddLayout(num):

    data = [["                            " for col in range(2)]for row in range(3)]
    Websites = []
    websitesKey = []
    getWebsitesQuery = """SELECT * FROM Websites"""
    Results = cursor.execute(getWebsitesQuery).fetchall()
    for result in Results:
        Websites.append(result[1])
        websitesKey.append(result[0])

    layout = [
        [gui.Text("Your Current Wishlist:", key=f'__CurrentPrompt__{num}')],
        [gui.Table(data, headings=["Item", "Desired Price"], key=f'__Data__{num}')],
        [gui.Button("Remove Selected Item", key=f'__Remove__{num}', size=(46, 1))],
        [gui.Button("Edit Selected Item", key=f'__Edit__{num}', size=(46, 1))],
        [gui.Text("__________________________________________", key=f'Divider{num}')],
        [gui.Text("Add Another Item: ", key=f'AddPrompt{num}')],
        [gui.Text("What Website Is It On?:                                    ", key=f'WebPrompt{num}'), gui.Combo(Websites, key=f'__Website__{num}')],
        [gui.Text("What Is The Name Of The Item?:                        ", key=f'NamePrompt{num}'), gui.InputText(key=f'__Name__{num}', size=(16,1))],
        [gui.Text("What Price Do You Want To Pay For This Item?: ", key=f'PricePrompt{num}'), gui.InputText(key=f'__Price__{num}', size=(16,1))],
        [gui.Button("Search And Add This Item", key=f'__Add__{num}', size=(46, 1))],
        [gui.Text("____________________________________________________________________________", key=f'SecondBarrier{num}')],
        [gui.Button("Push Notifications", key=f'__Notify__{num}', size=(46, 1))]
    ]
    return layout, num, Websites, websitesKey


def getPriceUpdateLayout(num):
    layout = [
        [gui.Text("Update the desired price of", key=f'UpdateIntroText{num}'), gui.Text("", key=f'__ItemName__{num}', size=(20,1))],
        [gui.Text("New Price: ", key=f'NewPricePrompt{num}'), gui.InputText(key=f'__NewPrice__{num}')],
        [gui.Submit("Update Price", key=f'__Update__{num}', size=(40, 1))]
    ]
    return layout, num


def addItem():
    global windowsLoaded

    layout, refNum, websites, websitesKey = getAddLayout(windowsLoaded)

    addWindow = gui.Window("Add Items To Your Watchlist", layout, finalize=True)
    itemsTable, itemsKey = getItemsTable()
    addWindow[f'__Data__{refNum}'].update(itemsTable)

    while True:
        event, values = addWindow.read()

        if event in [gui.WIN_CLOSED, f'__Exit__{refNum}']:
            break
        
        if event == f'__Add__{refNum}':
            valuesDict = {"ItemName":values[f'__Name__{refNum}'], "DesiredPrice":values[f'__Price__{refNum}'], "Website":values[f'__Website__{refNum}']}
            validateInput(valuesDict, websites, websitesKey)
            itemsTable, itemsKey = getItemsTable()
            addWindow[f'__Data__{refNum}'].update(itemsTable)

        if event == f'__Notify__{refNum}':
            autoCheck.CheckPrice()
        
        if event == f'__Remove__{refNum}':
            itemIndex = values[f'__Data__{refNum}'][0]
            itemId = itemsKey[itemIndex]
            query = f"""DELETE FROM CheckMe WHERE CheckableID == {itemId}"""
            rusure = gui.popup_yes_no(f"Are You Sure You Want To Remove {itemsTable[values[f'__Data__{refNum}'][0]][0][0]}?")

            if rusure == "Yes":
                cursor.execute(query)
                itemsTable, itemsKey = getItemsTable()
                addWindow[f'__Data__{refNum}'].update(itemsTable)
        
        if event == f'__Edit__{refNum}':
            itemIndex = values[f'__Data__{refNum}'][0]
            itemId = itemsKey[itemIndex]
            updatePrice(itemId, itemsTable[values[f'__Data__{refNum}'][0]][0])
            itemsTable, itemsKey = getItemsTable()
            addWindow[f'__Data__{refNum}'].update(itemsTable)


def getItemsTable():
    Query = """SELECT CheckableID, Name, DesiredPrice FROM CheckMe"""
    results = cursor.execute(Query).fetchall()

    returnTable = []
    tableKey = []
    for result in results:
        returnTable.append([[str(result[1])][0], [str(result[2])]])
        tableKey.append(result[0])
    return returnTable, tableKey


def validateInput(values, websites, webkeys):
    emptyField = False
    continue_ = True
    for value in values:
        if not value:
            emptyField = True
    if not emptyField:
        websiteId = webkeys[websites.index(values['Website'])]

        try:
            values['DesiredPrice'] = float(values['DesiredPrice'].strip("$"))
        except ValueError:
            gui.popup("Please Enter A Valid Price")
            continue_ = False
        
        if continue_:
            if values['Website'] == "IsThereAnyDeal":
                appendITAD(values, websiteId)
            

def appendITAD(values, websiteId):
    global headers

    try:
        itemname = "+".join(values['ItemName'].split())
        url = f"https://isthereanydeal.com/search/?q={itemname}"
        html = bs(requests.get(url, headers=headers).content, 'html.parser')
        suburl = html.find_all(class_="card-container")[0].find(class_= "card__img").get('href')
        name = html.find_all(class_="card-container")[0].find(class_="card__title").find(text=True)
        link = f"https://isthereanydeal.com{suburl}"

        insertQuery = f"""INSERT INTO CheckMe (Name, Url, DesiredPrice, WebsiteID) VALUES ("{name}", "{link}", "${values['DesiredPrice']}", "{websiteId}")"""
        check = gui.popup_yes_no(f"We Found {name}, would you like to add it with the desired price of ${values['DesiredPrice']}?")

        if check == "Yes":
            cursor.execute(insertQuery)
            db.commit()
    except IndexError:
        gui.popup("We could not find any game by that name in our system :(")


def updatePrice(id_, name):
    global windowsLoaded

    layout, refNum = getPriceUpdateLayout(windowsLoaded)
    windowsLoaded += 1
    updateWindow = gui.Window("update Price", layout, finalize=True)
    print(name)
    updateWindow[f'__ItemName__{refNum}'].update(name)
    while True:
        event, values = updateWindow.read()

        if event == f'__Update__{refNum}':
            try:
                newPrice = float(values[f'__NewPrice__{refNum}'].strip("$"))
                query = f""" UPDATE CheckMe SET DesiredPrice = "${newPrice}" WHERE CheckableID = {id_} """
                cursor.execute(query)
                db.commit()
                gui.popup_ok("ok, the price was updated")
                updateWindow.close()
                break
            except ValueError:
                gui.popup_ok("please enter a valid price")

        if event in [gui.WIN_CLOSED, f'EXIT{refNum}']:
            break


addItem()
input("")