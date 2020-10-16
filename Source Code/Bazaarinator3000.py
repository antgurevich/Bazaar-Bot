import requests, time, os, json
import tkinter as tk
from tkinter import messagebox, font, HORIZONTAL, RIGHT, Y, END, MULTIPLE, font
from configparser import ConfigParser
###########################################################################
version="v.0.1.0"
apiKey="[REDACTED]" #Run /api new in Hypixel to receive your own API key
config_object=ConfigParser()
###########################################################################
def changeLog(): #Shows the Change Log
    changeLogUI=tk.Tk()
    changeLogUI.geometry("600x400")
    changeLogUI.title("Change Log")
    logList=[]

    scroll_bar=tk.Scrollbar(changeLogUI) #Creates scroll wheel
    scroll_bar.pack(side=RIGHT,fill=Y)
    changeLogListBox=tk.Listbox(changeLogUI,yscrollcommand=scroll_bar.set,width=80,height=20,bg="SystemButtonFace",bd=0)

    vText=tk.Label(changeLogUI,text=("Current version: "+str(version)),font=("Arial",15)) #Text with version info (shown at top)
    vTextFont=font.Font(vText, vText.cget("font"))
    vTextFont.config(underline=True)
    vText.config(font=vTextFont)
    vText.pack()
    
    logList.append("0.1.0 (10/16/2020): Initial functional version released")
    
    for item in logList:
        changeLogListBox.insert(END,item)
        changeLogListBox.pack()

    scroll_bar.config(command=changeLogListBox.yview)
    tk.Button(changeLogUI,command=changeLogUI.destroy,text="Return").pack()

    changeLogUI.mainloop()
###########################################################################
def getData(): #Pulls data from API into dictionary
    global bazaarData, productNames   
    bazaarData = requests.get("https://api.hypixel.net/skyblock/bazaar?key="+apiKey).json()
    productNames=bazaarData["products"].keys()
###########################################################################
def resultOutput(changeList): #Displays results (Shows errorbox if no changes)
    if len(changeList)!=0: #Runs if there are results
        results=tk.Tk()
        results.title("Results")
        results.geometry("500x500")
        results.resizable(0,0)
        
        scroll_bar=tk.Scrollbar(results)
        scroll_bar.pack(side=RIGHT,fill=Y)
        resultsListBox=tk.Listbox(results,yscrollcommand=scroll_bar.set,selectmode=MULTIPLE,width=90,height=40)
        tk.Button(results,text="Return",command=results.destroy).pack()

        for item in changeList:
            resultsListBox.insert(END, item)
            resultsListBox.pack()
            scroll_bar.config(command=resultsListBox.yview)
        
        results.mainloop()
    else: #No significant changes were made
        messagebox.showerror("No Results","There were no significant changes in price")

    exportPriceData()
###########################################################################
def initialCheck(): #Checks if it was the initial time running the program
    global oldProductDict
    path=os.getcwd()
    if os.path.exists(path+"\B3kData.json"):
        importOldData()
    else: #Runs if it is the first time running program or data couldn't be fetched
        getData()
        for product in productNames:
            instantSellPrice = bazaarData["products"][product]["quick_status"]["sellPrice"]
            instantSellPrice=round(instantSellPrice,2)
            instantBuyPrice = bazaarData["products"][product]["quick_status"]["buyPrice"]
            instantBuyPrice=round(instantBuyPrice,2)

            oldProductDict[product]={"InstantBuy":instantBuyPrice,"InstantSell":instantSellPrice}
        exportPriceData()
        messagebox.showerror("Initial Check Complete","Initial values set")
###########################################################################
def exportPriceData(): #Saves productDict to B3kData.json
    with open("B3kData.json","w") as dataJson:
        json.dump(oldProductDict,dataJson,indent=4)
###########################################################################
def importOldData(): #Reads data from B3kData.json and saves to oldProductDict
    global oldProductDict
    with open("B3kData.json") as json_file:
        oldProductDict=json.load(json_file)
###########################################################################
def checkPrices(): #Calculates whether the instant buy/sell has changed by 10%+
    global productDict,oldProductDict
    getData()
    readSettings()
    changeList=[]
    importOldData()

    print (changePercent)
    negChangePercent=(changePercent/-1) #Used where a negative change percent is needed

    for product in productNames: #Runs calculation for every product in Bazaar
        instantSellPrice = bazaarData["products"][product]["quick_status"]["sellPrice"]
        instantSellPrice=round(instantSellPrice,2)
        instantBuyPrice = bazaarData["products"][product]["quick_status"]["buyPrice"]
        instantBuyPrice=round(instantBuyPrice,2)

        productDict[product]={"InstantBuy":instantBuyPrice,"InstantSell":instantSellPrice}
        oldSellPrice=(oldProductDict[product]["InstantSell"])
        oldBuyPrice=(oldProductDict[product]["InstantBuy"])

        try:
            sellChange=round((((instantSellPrice-oldSellPrice)/oldSellPrice)*100),2)
            buyChange=round((((instantBuyPrice-oldBuyPrice)/oldBuyPrice)*100),2)
            
            if sellChange<negChangePercent: #Instant sell price decreased by x%
                changeList.append(str(product)+"'s sell price has decreased by "+str(sellChange)+"%")
                changeList.append(str(product)+": Instant Sell: $"+str(instantSellPrice)+" Instant Buy: $"+str(instantBuyPrice))
            
            elif sellChange>changePercent: #Instant sell price increased by x%
                changeList.append(str(product)+"'s sell price has increased by "+str(sellChange)+"%")
                changeList.append(str(product)+": Instant Sell: $"+str(instantSellPrice)+" Instant Buy: $"+str(instantBuyPrice))
            
            if buyChange<negChangePercent: #Instant buy price decreased by x%
                changeList.append(str(product)+"'s buy price has decreased by "+str(buyChange)+"%")
                changeList.append(str(product)+": Instant Sell: $"+str(instantSellPrice)+" Instant Buy: $"+str(instantBuyPrice))
            
            elif buyChange>changePercent: #Instant buy price increased by x%
                changeList.append(str(product)+"'s buy price has increased by "+str(buyChange)+"%")
                changeList.append(str(product)+": Instant Sell: $"+str(instantSellPrice)+" Instant Buy: $"+str(instantBuyPrice))
    
        except Exception as error: 
            print ("Error=",error, product)
             
        #print (productDict['NETHERRACK']["InstantBuy"])
    exportPriceData()
    oldProductDict=productDict
    resultOutput(changeList)
        #time.sleep(300)
###########################################################################
def readSettings(): #Reads settings from B3kSettings.ini
    global changePercent
    try:
        config_object.read("B3kSettings.ini")
        userSettings=config_object["Settings"]
        changePercent=int(userSettings["ChangePercent"])
    except: #Default change percent is 10
        changePercent=10
###########################################################################
def saveSettings(): #Saves settings to B3kSettings.ini
    try:
        if confirmPopUp=="yes": #If user selected to reset settings (Routed from resetSettings())
            changePercent=10
    except: #User clicked Save & Exit
        changePercent=percentScale.get()

    config_object["Settings"]={
        "ChangePercent": changePercent
    }
    with open ("B3kSettings.ini","w") as conf:
        config_object.write(conf)

    settingsUI.destroy()
###########################################################################
def resetSettings(): #Resets all settings if user selects "Yes" in the popup
    global changePercent, confirmPopUp

    confirmPopUp=messagebox.askquestion("Confirm","Are you sure you want to reset all settings?")
    
    if confirmPopUp=="yes": #Runs if user wants to reset all settings
        changePercent=10
        saveSettings()
        print (True)
    else:
        settingsUI.destroy()
        settings()
###########################################################################
def settings(): #Settings menu
    global percentScale, settingsUI
    settingsUI=tk.Tk()
    settingsUI.geometry("300x200")
    settingsUI.title("Settings")

    tk.Label(settingsUI,text="Percent Change Criteria").pack()
    
    readSettings()
        
    percentScale=tk.Scale(settingsUI, from_=1, to=500, orient=HORIZONTAL,variable=changePercent,length=250)
    percentScale.set(changePercent) #Auto set to 10 if no data is found
    percentScale.pack()

    tk.Button(settingsUI,text="Reset all settings",command=resetSettings).place(x=100,y=100)

    tk.Button(settingsUI,text="Save & Exit",command=saveSettings,fg="green").place(x=70,y=150)
    tk.Button(settingsUI,text="Cancel",command=settingsUI.destroy,fg="red").place(x=180,y=150)

    settingsUI.mainloop()
###########################################################################
def mainMenu(): #Loads main menu
    menu=tk.Tk()
    menu.title("Bazaarinator 3000")
    menu.geometry("600x400")
    menu.resizable(0,0)

    tk.Label(menu,text="Bazaarinator 3000",font=("Pristina",50)).place(x=70,y=30)
    tk.Label(menu,text="Created by Anton Gurevich",font=("",10)).place(x=200,y=100)
    tk.Label(menu,text=version).place(x=560,y=380)
    
    tk.Button(menu,text="Run Check",command=checkPrices,fg="green",font=("",25)).place(x=60,y=250)
    tk.Button(menu,text="Settings",command=settings,font=("",25)).place(x=260,y=250)
    tk.Button(menu,text="Quit",command=menu.destroy,fg="red",font=("",25)).place(x=420,y=250)
    tk.Button(menu,text="Change Log",command=changeLog,font=("",10)).place(x=5,y=370)

    menu.mainloop()
###########################################################################
#Main program
productDict={}
oldProductDict={}

initialCheck()
readSettings()
mainMenu()    
