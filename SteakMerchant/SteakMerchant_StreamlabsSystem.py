#---------------------------------------
#   Import Libraries
#---------------------------------------
import os
import codecs
import json
import random as rand
import time as t

#---------------------------------------
#   [Required]  Script Information
#---------------------------------------
ScriptName = "Steak Merchant"
Website = ""
Creator = "Franken Steak"
Version = "1.9"
Description = "This script are are sell very many items (/O.O)/"

#---------------------------------------
#   Set Variables
#---------------------------------------
SettingsFile = os.path.join(os.path.dirname(__file__), "FSSettings.json")
ScriptSettings = None                                                                                                   #Settings to be used from chatbot interface

sPath = None                                                                                                            #The path to which the .txt's will be saved

#customer related
sCurrCustomer = None                                                                                                    #the current customer being serviced
pCurrCustomer = None
arrSCustomers = None                                                                                                    #the customers that have been serviced in this instance of the program
sExclusionList = None

#item related
sPathItems = None
iArrItems = None                                                                                                        #all the items
iArrShopItems = None                                                                                                    #the items being sold

#inverntory related
arrSInventory = None                                                                                                    #names of players accessing inventory atm
arrPInventory = None                                                                                                    #players accessing inventory atm

#timer related
tMerchCD = None                                                                                                         #the cooldown for The merchant
tLastMerch = None                                                                                                       #time the last merch happened
tTickCD = None                                                                                                          #the cooldown for tick()
tLastTick = None                                                                                                        #time the last tick() executed

#fish related
activeFish = None
recFish1 = None
recFish2 = None 

#heist related
iHeistLim = None
iHeistTmr1 = None                                                                                                       #time between heists
tHeistTmr1 = None                                                                                                       #timer till next heist
bHeistTmr1 = None
iHeistTmr2 = None                                                                                                       #time to enter heist
tHeistTmr2 = None                                                                                                       #timer till heist starts
bHeistTmr2 = None

lHeisters = None                                                                                                        #list of heisters participating in current heist
lHInput = None                                                                                                          #list of money each heister as input into the pool
lHCNames = None                                                                                                         #list of names that have modified win chances
lHCChance = None                                                                                                        #list of chances to win for each modified name

deaths = None

#---------------------------------------
#   Classes
#---------------------------------------
class Settings(object):
    """ Load in saved settings file if available else set default values. """
    def __init__(self, settingsfile=None):
        try:
            with codecs.open(SettingsFile, encoding="utf-8-sig", mode="r") as f:
                self.__dict__ = json.load(f, encoding="utf-8")
            self.initSuccess = True
        except:
            # load in variables from .json file if it fails to load
            self.initSuccess = False


    def reload(self, jsondata):
        """ Reload settings from Chatbot user interface by given json data. """
        self.__dict__ = json.loads(jsondata, encoding="utf-8")
        return

    def save(self, settingsfile):
        """ Save settings contained within to .json and .js settings files. """
        try:
            with codecs.open(SettingsFile, encoding="utf-8-sig", mode="w+") as f:
                json.dump(self.__dict__, f, encoding="utf-8")
            with codecs.open(SettingsFile.replace("json", "js"), encoding="utf-8-sig", mode="w+") as f:
                f.write("var settings = {0};".format(json.dumps(self.__dict__, encoding='utf-8')))
        except:
            Parent.Log(ScriptName, "Failed to save settings to file.")
        return

class Player: #DONE ???
    #INITIALIZE PLAYER##################################################################################################
    def __init__(self):
        # player equipped
        self.itemArrEquipped = []

        # player stats
        self.iPlayerStats = []

        # player inventory
        self.itemArrInventory = []
        self.iInvSize = 7

        #merchant menu
        self.iMerchMenu = -1
        self.iMerchItem = -1
        self.bSecretRoom = False

        #inventory menu
        self.iInvMenu = -1
        self.iInvItem = -1

        # player item related
        self.bFirstMsg = False
        return

    #REFRESH PLAYER#####################################################################################################
    def refreshPlayer(self, sPlayerName, sPath):
        sTmp = sPath + sPlayerName + ".txt"                                                                         #get path to player file
        try:
            #   STEP 1: Import file
            if (os.path.isfile(sTmp)):
                fileTmp = open(sTmp, "r")

                fileTmp.readline()
                for i in range(0, 5):
                    sTmp2 = fileTmp.readline()
                    self.itemArrEquipped.append(str(sTmp2[3:len(sTmp2)-1]))

                fileTmp.readline()

                sTmp2 = fileTmp.readline()
                self.iInvSize = int(sTmp2[:len(sTmp2)-1])
                
                for i in range(0, self.iInvSize):
                    sTmp2 = fileTmp.readline()
                    self.itemArrInventory.append(str(sTmp2[3:len(sTmp2)-1]))

                fileTmp.readline()

                for i in range(0, 23):
                    sTmp2 = fileTmp.readline()
                    self.iPlayerStats.append(int(sTmp2[4:len(sTmp2)-1]))

                fileTmp.close()

            else:
                fileTmp = open(sTmp, "a")
                fileTmp.close()

                fileTmp = open(sTmp, "r+")
                fileTmp.write("-EQUIPPED\n1: \n2: \n3: \n4: \n5: \n") #head, chest, legs, weapon, ??
                for i in range(0, 5):
                    self.itemArrEquipped.append("")

                fileTmp.write("-INVENTORY\n7\n1: \n2: \n3: \n4: \n5: \n6: \n7: \n")
                for i in range(0, 7):
                    self.itemArrInventory.append("")

                fileTmp.write("-STATS\n01: 0\n02: 0\n03: 0\n04: 0\n05: 0\n06: 0\n07: 0\n08: 0\n09: 0\n10: 0\n11: 0\n12: 0\n13: 0\n14: 0\n15: 0\n16: 0\n17: 0\n18: 0\n19: 0\n20: 0\n21: 0\n22: 0\n23: 0\n")
                for i in range(0, 23):
                    self.iPlayerStats.append(0)

                fileTmp.close()

        except:
            Parent.SendTwitchWhisper(sPlayerName, "An error occured with the merchant script. Please whisper I_am_steak that ''error QuadrupleEye'' occured")
            fileTmp.close()

        return

    def updatePlayer(self, sPlayerName):
        global sPath
        sTmp = sPath + str(sPlayerName) + ".txt"
        try:
            if (os.path.isfile(sTmp)):
                fileTmp = open(sTmp, "w")

                fileTmp.write("-EQUIPPED\n")
                for i in range(0, 5):
                    sTmp2 = str(i) + ": " + self.itemArrEquipped[i] + "\n"
                    fileTmp.write(sTmp2)

                fileTmp.write("-INVENTORY\n")
                fileTmp.write(str(self.iInvSize) + "\n")
                for i in range(0, self.iInvSize):
                    sTmp2 = str(i) + ": " + self.itemArrInventory[i] + "\n"
                    fileTmp.write(sTmp2)

                fileTmp.write("-STATS\n")
                for i in range(0, len(self.iPlayerStats)):
                    sTmp2 = str(i) + ": " + str(self.iPlayerStats[i]) + "\n"
                    if (i < 10):
                        sTmp2 = "0" + sTmp2
                    fileTmp.write(sTmp2)

                fileTmp.close()

            else:
                sTmp = "An error occured in the merchant script please whisper i_am_steak \"Error: Blood moon\" thank you"
                Parent.SendTwitchWhisper(sPlayerName, sTmp)

        except:
            sTmp = "An error occured in the merchant script please whisper i_am_steak \"Error: Blood moon 2 - the bloodier moon\" thank you"
            Parent.SendTwitchWhisper(sPlayerName, sTmp)

        return

    #CLEAR FUNCTION#####################################################################################################
    def clear(self):
        # player equipped
        self.itemArrEquipped = []

        # player stats
        self.iPlayerStats = []

        # player inventory
        self.itemArrInventory = []
        self.iInvSize = 7

        #merchant menu
        self.iMerchMenu = -1
        self.iMerchItem = -1
        self.bSecretRoom = False

        #inventory menu
        self.iInvMenu = -1
        self.iInvItem = -1

        # player item related
        self.bFirstMsg = False
        return

    #ITEM FUNCTIONS#####################################################################################################
    def newInvItem(self, iSlot, sName):
        self.itemArrInventory[iSlot] = sName
        return

    def deletInvItem(self, iSlot):
        self.itemArrInventory[iSlot] = ""
        return

    def deleteEqpItem(self, iSlot):
        self.itemArrEquipped[iSlot] = ""
        return

    def removeItemStats(self, item):
        for i in range(0, len(item.iItemAttributes)):
            if (i < len(self.iPlayerStats)):
                self.iPlayerStats[i] = self.iPlayerStats[i] - item.iItemAttributes[i]
        return

    def addItemStats(self, item):
        for i in range(0, len(item.iItemAttributes)):
            if (i < len(self.iPlayerStats)):
                self.iPlayerStats[i] = self.iPlayerStats[i] + item.iItemAttributes[i]
        return

    def swapItems(self, eqpItem, invItem):
        sTmp = self.itemArrEquipped[eqpItem]
        self.itemArrEquipped[eqpItem] = self.itemArrInventory[invItem]
        self.itemArrInventory[invItem] = sTmp
        return

    def changeMsg(self):
        self.bFirstMsg = True

class Item: #DONE
    def __init__(self):
        # item name
        self.sItemName = ""

        # item attributes
        self.iItemTier = 0
        self.iItemAttributes = []
        self.iItemPrice = 0
        self.iItemPosition = -1
        self.sItemDescription = ""

        return

#---------------------------------------
#   [Required] Intialize Data 
#---------------------------------------
def Init():
    """
        Init is a required function and is called the script is being loaded into memory
        and becomes active. In here you can initialize any data your script will require,
        for example read the settings file for saved settings.
    """

    #   GLOBALS
    global sPath
    global sCurrCustomer
    global pCurrCustomer
    global arrSCustomers
    global sExclusionList

    global sPathItems
    global iArrItems
    global iArrShopItems

    global arrSInventory
    global arrPInventory

    global tMerchCD
    global tLastMerch
    global tTickCD
    global tLastTick

    global activeFish
    global recFish1
    global recFish2

    global iHeistLim
    global iHeistTmr1
    global tHeistTmr1
    global bHeistTmr1
    global iHeistTmr2
    global tHeistTmr2
    global bHeistTmr2

    global lHeisters
    global lHInput
    global lHCNames
    global lHCChance

    global deaths

    #   CODE
    sPath = os.path.dirname(os.path.abspath(__file__)) + "\\Players\\"
    sCurrCustomer = ""
    pCurrCustomer = Player()
    arrSCustomers = []
    sExclusionList = []
    importExclusions()

    sPathItems = os.path.dirname(os.path.abspath(__file__)) + "\\Items\\"
    iArrItems = []
    iArrShopItems = []
    importItems()

    arrSInventory = []
    arrPInventory = []

    tMerchCD = 300                                                                                                      #set merchant cooldown to 5 m ****
    tLastMerch = t.time() - tMerchCD
    tTickCD = 5                                                                                                         #set tick cooldown to 5 s
    tLastTick = t.time() - tTickCD

    activeFish = False
    recFish1 = 0
    recFish2 = ""

    iHeistLim = 15
    iHeistTmr1 = 120                                                                               #time between heists
    tHeistTmr1 = t.time()
    bHeistTmr1 = False
    iHeistTmr2 = 60                                                                                 #time before heist starts
    tHeistTmr2 = t.time()
    bHeistTmr2 = False

    lHeisters = []
    lHInput = []
    lHCNames = []
    lHCChance = []
    return

def importItems(): #DONE
    global sPathItems
    global iArrItems

    #   STEP 1: Check if item list exists
    Parent.SendTwitchMessage("Importing Items")
    sTmp = sPathItems + "itemList.txt"
    if (os.path.isfile(sTmp)):
        #   1.2: ye - get items names from items list
        fileTmp = open(sTmp, "r")                                                                                       #open item list

        sTmp2 = fileTmp.readline()
        iNumItems = int(sTmp2[:len(sTmp2)-1])                                                                           #get number of items

        for i in range(2, iNumItems+2):
            tmpItem = Item()

            sTmp2 = fileTmp.readline()
            tmpItem.sItemName = sTmp2[:len(sTmp2)-1]
            iArrItems.append(tmpItem)

        fileTmp.close()
    else:
        #   1.1: no - no item list we give up lol
        return

    Parent.SendTwitchMessage("Importing Item Attributes")
    #   STEP 2: Iterate through item list importing stats

    iErrors = 0
    for i in range(0, len(iArrItems)):
        tmpItem = iArrItems[i]
        sTmp = sPathItems + tmpItem.sItemName + ".txt"

        if (os.path.isfile(sTmp)):
            fileTmp = open(sTmp, "r")
            fileTmp.readline()
            for j in range(2, 25): #read stats
                sTmp2 = fileTmp.readline()
                tmpItem.iItemAttributes.append(int(sTmp2[:len(sTmp2)-1]))

            sTmp2 = fileTmp.readline() #read price
            tmpItem.iItemPrice = int(sTmp2[:len(sTmp2)-1])
            sTmp2 = fileTmp.readline() #read tier
            tmpItem.iItemTier = int(sTmp2[:len(sTmp2)-1])
            sTmp2 = fileTmp.readline() #read position
            tmpItem.iItemPosition = int(sTmp2[:len(sTmp2)-1])
            sTmp2 = fileTmp.readline() #read description
            tmpItem.sItemDescription = sTmp2[:len(sTmp2)-1]
            fileTmp.close()
        else:
            iErrors = iErrors + 1


    Parent.SendTwitchMessage("Items Imported: " + str(iErrors) + " errors")

def importExclusions(): #DONE
    global sExclusionList
    global sPath

    Parent.SendTwitchMessage("Importing Exclusions")
    sTmp = sPath + "ImeanTechnicallySpeakingifSomeoneHasthisnameontwitchitwouldfuckwiththeprogram.txt"

    if (os.path.isfile(sTmp)):
        with open(sTmp, "r") as fileTmp:

            iTmp = 0
            for line in fileTmp:
                iTmp = iTmp + 1
                sExclusionList.append(line[:len(line)-1])

            Parent.SendTwitchMessage(str(iTmp) + " exclusions imported")
    else:
        fileTmp = open(sTmp, "a")
        fileTmp.close()

#---------------------------------------
#   [Required] Execute Data / Process Messages
#---------------------------------------
def Execute(data): #TO EDIT
    """
        Execute is a required function that gets called when there is new data to be
        processed. Like a Twitch or Discord chat messages or even raw data send from
        Twitch IRC. This function will _not_ be called when the user disabled the script
        with the switch on the user interface.
    """

    #   GLOBALS
    global sPath
    global sCurrCustomer

    global arrSInventory
    global arrPInventory

    #   CODE
    #   STEP 1: MERCHANT
    """if (data.IsWhisper() and data.IsFromTwitch()):            #and Parent.IsLive()                                      #check if whisper from twitch while stream is live
        if (data.User == sCurrCustomer):
            try:
                merchant(data.Message)
            except Exception as e:
                Parent.SendTwitchWhisper("i_am_steak", e.message)
                Parent.SendTwitchWhisper("fsteak_bot", e.message)
        else:
            try:
                inventory(data.Message, data.User)
            except Exception as e:
                Parent.SendTwitchWhisper("i_am_steak", e.message)
                Parent.SendTwitchWhisper("fsteak_bot", e.message)
    """
    if (data.IsChatMessage() and data.IsFromTwitch()):# and Parent.IsLive()
        points4Messages(data.User, data.Message)
        fish(data)
        heist(data)
    return

def points4Messages(sUser, sMessage):
    global sPath

    global arrSInventory
    global arrPInventory

    try:
        #   STEP 1: EGG
        if (sMessage == "I am steak"):
            Parent.SendTwitchMessage("VoHiYo")

            if (sUser == "i_am_steak"):
                Parent.AddPoints(sUser, 500)

        #   STEP 2: POINTS PER CHAT MESSAGE
        if (sMessage[0] != '!'):
            if (sUser not in arrSInventory):
                newCustomer = Player()
                newCustomer.refreshPlayer(sUser, sPath)
                newCustomer.iInvMenu = 0

                arrPInventory.append(newCustomer)
                arrSInventory.append(sUser)

            tmpCustard = arrPInventory[arrSInventory.index(sUser)]

            #   STEP 2.1: First message payout
            if (tmpCustard.bFirstMsg == False):
                tmpCustard.changeMsg()
                iTmp = tmpCustard.iPlayerStats[14]
                if (iTmp != 0):
                    if (iTmp > 0):
                        Parent.AddPoints(sUser, iTmp)
                    else:
                        Parent.RemovePoints(sUser, iTmp)

            #   STEP 2.2: Possible message payout
            iTmp = tmpCustard.iPlayerStats[15]
            if (iTmp > 0):
                iTmp2 = rand.randint(0, 200)
                if (iTmp2 <= iTmp):
                    Parent.AddPoints(sUser, 2)

            #   STEP 2.3: Static message payout
            iTmp = 1 + tmpCustard.iPlayerStats[16]
            if (iTmp > 0):
                Parent.AddPoints(sUser, iTmp)
            else:
                Parent.RemovePoints(sUser, -1*iTmp)


    except Exception as e:
        Parent.SendTwitchWhisper("i_am_steak", e.message)
        Parent.SendTwitchWhisper("fsteak_bot", e.message)
    return
   
def fish(data):
    global activeFish
    global recFish1
    global recFish2

    #PART 1: FISH SWITCH
    if (((data.User == "tiltasaurus") or (data.User == "i_am_steak")) and (data.Message == '!fish')):             #check if !fish
        if (activeFish == False):
            activeFish = True                                                                                       #allow fish to be caught
            sTmp = "A school of fish is passing through a lake nearby! Type any message with 'fish' in it to see if you can catch one."
            Parent.SendTwitchMessage(sTmp)
            Parent.SendDiscordMessage(sTmp)
        else:
            sTmp = "The school of fish has passed! The largest fish caught was worth " + str(recFish1) + " and was caught by " + recFish2 + "."
            Parent.SendTwitchMessage(sTmp)
            Parent.SendDiscordMessage(sTmp)
            activeFish = False
            recFish1 = 0
            recFish2 = ""

    #PART 2: FISH
    if (activeFish == True):
        if ((("SabaPing" in data.Message) or ("fish" in data.Message)) and (data.Message != "fish")):                       #check if message contains "fish"
                
            i = rand.randint(1, 200)
            rand.seed(t.time() + recFish1 + i)

            i = rand.randint(1, 100)                                                                                #45% chance to catch a fish
            if (i < 25):                                                                                        
                Parent.SendTwitchMessage("PowerUpL SabaPing PowerUpR")

                i = rand.randint(1, 100)                                                                            #get fish size
                sTmp = data.User + " found a rare Tilted Herring worth " + str(i) + " points!"
                Parent.SendTwitchMessage(sTmp)

                Parent.AddPoints(data.User, i)

                if (i > recFish1):                                                                                  #check if largest fish
                    recFish1 = i
                    recFish2 = data.User

def heist(data):
    global iHeistLim
    global iHeistTmr1
    global tHeistTmr1
    global bHeistTmr1
    global iHeistTmr2
    global tHeistTmr2
    global bHeistTmr2

    global lHeisters
    global lHInput
    global lHCNames
    global lHCChance

    ### CODE
    if (len(data.Message) > 7):
        sTmp = ""
        for i in range(0, 6):
            sTmp = sTmp + data.Message[i]

        if ((sTmp == "!heist") and (bHeistTmr1 == False)):                                          #check if !heist and heist not on cd
            
            sTmp = ""
            for i in range(7, len(data.Message)):
                sTmp = sTmp + data.Message[i]

            try:
                iTmp = int(sTmp)
                lTmp = long(sTmp)

                if ((len(lHeisters) == 0) and (iTmp > 0)):                                                           #check if there are currently no heisters
                    sTmp = data.User + " is trying to get a team together in order to hit the nearest bank. The heist will take place in one minute, in order to join type !heist (amount)."
                    Parent.SendTwitchMessage(sTmp)
                    Parent.SendDiscordMessage(sTmp)

                    tHeistTmr2 = t.time() + iHeistTmr2
                    bHeistTmr2 = True

                if ((len(lHeisters) <= iHeistLim) and (data.User not in lHeisters) and (iTmp > 0)):

                    if (Parent.GetPoints(data.User) > lTmp):
                        Parent.RemovePoints(data.User, lTmp)

                        lHInput.append(iTmp)
                        lHeisters.append(data.User)

                        if (len(lHeisters) > 1):
                            sTmp2 = data.User + " has joined the heist with " + str(iTmp) + " TiltCoins!"
                            Parent.SendTwitchMessage(sTmp2)
                            Parent.SendDiscordMessage(sTmp2)

            except:
                sTmp = ""
        elif ((sTmp == "!heist") and (bHeistTmr1 == True)):
            fTmp = tHeistTmr1 - t.time()
            iMin = int(fTmp)/60
            sTmp = data.User + " you will be able to heist again in " + str(iMin) + " minutes"
            Parent.SendTwitchMessage(sTmp)
            Parent.SendDiscordMessage(sTmp)
    return

#---------------------------------------
#   [Required] Tick Function
#---------------------------------------
def Tick(): #DONE
    """
        Tick is a required function and will be called every time the program progresses.
        This can be used for example to create simple timer if you want to do let the
        script do something on a timed basis.This function will _not_ be called when the
        user disabled the script with the switch on the user interface.
    """

    #   GLOBALS
    global tTickCD
    global tLastTick

    tTime = t.time()

    #   CODE
    if (tLastTick + tTickCD <= tTime):
        tLastTick = tTime   
        #merchantTick()
        heistTick()

    return

def merchantTick():
    #   GLOBALS
    global tMerchCD
    global tLastMerch

    #   CODE                                                                                            #update tick() timer
    #   STEP 1: Check if new merch
    if (tLastMerch + tMerchCD <= t.time()):
        #   GLOBALS
        global sPath

        global sCurrCustomer
        global pCurrCustomer
        global arrSCustomers

        global sExclusionList

        tLastMerch = t.time()                                                                                          #update last sale time

        #   CODE
        #   STEP 2: Check if busy with a customer
        if (sCurrCustomer != ""):   

            #   STEP 2.1: Say goodbye to current customer
            sTmp = "Thanks for browsing, but I gotta get going. See ya later kid"
            Parent.SendTwitchWhisper(sCurrCustomer, sTmp)

            sCurrCustomer = ""
            pCurrCustomer.clear()


        #   STEP 3: Find new customer
        for i in range(0, 25):

            #   STEP 3.1: Get random active user
            sNewCustomer = ""
            try:
                sNewCustomer = str(Parent.GetRandomActiveUser()).lower()                                                             #get random active twitch user
            except:
                sNewCustomer = ""

            #   STEP 3.2: Check if user has been serviced
            if ((sNewCustomer not in arrSCustomers) and (sNewCustomer != "i_am_steak") and (sNewCustomer != "") and (sNewCustomer not in sExclusionList)):

                #   STEP 3.3: Update new
                sCurrCustomer = sNewCustomer                                                                        #set new customer
                arrSCustomers.append(sNewCustomer)                                                                  #add new customer to serviced list
                pCurrCustomer.refreshPlayer(sCurrCustomer, sPath)
                pCurrCustomer.iMerchMenu = 0

                #   STEP 3.4: Send user message
                sTmp = "(Merchant) Pssssst, hey... Hey kid! Wanna buy some items? [1] yes - [2] no - [3] opt out of item script"
                Parent.SendTwitchWhisper(sCurrCustomer, sTmp)

                break
    return

def heistTick():
    #   GLOBALS
    global iHeistLim
    global iHeistTmr1
    global tHeistTmr1
    global bHeistTmr1
    global iHeistTmr2
    global tHeistTmr2
    global bHeistTmr2

    global lHeisters
    global lHInput
    global lHCNames
    global lHCChance

    ### CODE
    if ((bHeistTmr1 == True) and (t.time() > tHeistTmr1)):
        bHeistTmr1 = False                                                                          #reset heist timer
        sTmp = "It looks like the cops have given up searching for the perpetrators. You can now heist again using !heist (amount)."
        Parent.SendTwitchMessage(sTmp)
        Parent.SendDiscordMessage(sTmp)

    elif ((bHeistTmr2 == True) and (t.time() > tHeistTmr2)):
        bHeistTmr2 = False
        tHeistTmr1 = t.time() + iHeistTmr1
        bHeistTmr1 = True

        sTmp = "The heist has begun! Everyone gets ready with their various duties and checks their equipment before hopping out of the van and heading into the bank!"
        Parent.SendTwitchMessage(sTmp)
        Parent.SendDiscordMessage(sTmp)

        sList = []
        dList = []

        rand.seed(t.time() + len(lHeisters))
        iTmp = 0

        sOut = "Heist stats: "
        for i in range(0, len(lHeisters)):
            iTmp = rand.randint(0, 200)
            sOut = sOut + " #" + lHeisters[i] + " - " + str(iTmp)
            rand.seed(iTmp + t.time())

            if (lHeisters[i] in lHCNames):                                                                              #check if modified win chance
                j = 0
                for j in range(0, len(lHCNames)):
                    if (lHCNames[j] == lHeisters[i]):
                        break

                iTmp2 = lHCChance[j]
                sOut = sOut + "," + str(iTmp2) 

                if (iTmp > iTmp2):
                    sList.append(lHeisters[i])                                                                          #success achieved

                    if ((iTmp2 > 50) and (iTmp2 < 70)):                                                                 #reduce percent to win by 5%
                        iTmp2 = iTmp2 + 5
                        lHCChance[j] = iTmp2
                        sOut = sOut + ",1"

                    elif (iTmp2 < 50):                                                                                  #reset win chances
                        if (len(lHCNames) > 1):
                            lHCNames = lHCNames[0:j] + lHCNames[j+1:] 
                            lHCChance = lHCChance[0:j] + lHCChance[j+1:]
                            sOut = sOut + ",2"

                        else:
                            lHCNames = []
                            lHCChance = []
                            sOut = sOut + ",3"

                else:
                    dList.append(lHeisters[i])

                    if ((iTmp2 < 50) and (iTmp2 > 20)):                                                                 #reduce chance to lose by 10%
                        iTmp2 = iTmp2 - 10
                        lHCChance[j] = iTmp2
                        sOut = sOut + ",4"

                    elif (iTmp2 > 50):                                                                                  #reset win chances
                        if (len(lHCNames) > 1):
                            lHCNames = lHCNames[0:j] + lHCNames[j+1:] 
                            lHCChance = lHCChance[0:j] + lHCChance[j+1:]
                            sOut = sOut + ",5"

                        else:
                            lHCNames = []
                            lHCChance = []
                            sOut = sOut + ",6"

            else: 
                lHCNames.append(lHeisters[i])

                if (iTmp > 50):
                    sList.append(lHeisters[i])
                    lHCChance.append(55)

                else:
                    dList.append(lHeisters[i])
                    lHCChance.append(40)

        Parent.SendTwitchWhisper("i_am_steak", sOut)
        Parent.SendTwitchWhisper("fsteak_bot", sOut)

        if (len(sList) > 0):
            iTot = 0                                                                                #get total input currency
            for i in range(0, len(lHInput)):
                iTot = iTot + lHInput[i]

            iTot = int(iTot * 1.25)

            iSus = 0                                                                                #get total input currency of succesful
            for i in range(0, len(lHeisters)):
                if (lHeisters[i] in sList):
                    iSus = iSus + lHInput[i]

            sTmp = "Some of the crew got out of the bank with the loot! The results are: "
            j = 0
            for i in range(0, len(lHeisters)):

                if (lHeisters[i] in sList):
                    iTmp = int((float(lHInput[i])/iSus)*iTot)
                    Parent.AddPoints(lHeisters[i], iTmp)
                    sTmp = sTmp + lHeisters[i] + " (" + str(iTmp) + ")"
                    j = j + 1
                    if (j < len(sList)):
                        sTmp = sTmp + " - "

            Parent.SendTwitchMessage(sTmp)
            Parent.SendDiscordMessage(sTmp)

        if (len(dList) > 0):
            deaths = [" forgot how explosives worked leading to a \"tiny\" accident with the opening of the vault. The following crew members seem to have miraculously dissapeared: ",
                        " forgot to put a silencer on their gun causing a firefight amonst the crew and the bank guards. The following crew members were shot and killed: ",
                        " thought that carrying rocket launchers, guns, and explosives into a bank would go unnoticed causing a firefight amongst the crew and the bank guard. The following crew members were shot and killed: ",
                        " walked straight into a guard... needless to say this caused quite a comotion and thus a firefight broke out. The following crew members were shot and killed: ",
                        "An unamed vigilante was prowling the area and caught the following crew members: ",
                        "Upon exiting the bank with the loot a team of SWAT snipers opened fire on the crew, the following crew members died in the comotion: ",
                        "It seems one of the crew ratted us out and the cops knew we were coming, the following crew members were apprehended in the ambush: ",
                        " tilted their teammates causing the following crew members to give up on the heist: "]

            rand.seed(len(dList) + t.time())
            iTmp = rand.randint(0, 2*(len(deaths)-1)) - 1
            sTmp = deaths[iTmp]


            if (iTmp < 4):
                rand.seed(iTmp + t.time())
                iTmp = rand.randint(0, 2*len(lHeisters))
                sTmp = lHeisters[i] + sTmp

                for i in range(0, len(dList)):
                    sTmp = sTmp + dList[i]
                    if (i < len(dList) - 1):
                        sTmp = sTmp + ", "

                Parent.SendTwitchMessage(sTmp)
                Parent.SendDiscordMessage(sTmp)

            elif (iTmp < 7):
                for i in range(0, len(dList)):
                    sTmp = sTmp + dList[i] 
                    if (i < len(dList) - 1):
                        sTmp = sTmp + ", "

                Parent.SendTwitchMessage(sTmp)
                Parent.SendDiscordMessage(sTmp)
                
            else:
                sTmp2 = ""
                for i in range(0, len(dList)):
                    if (i < len(dList) - 1):
                        sTmp2 = sTmp2 + dList[i] + ", "
                    else:
                        sTmp2 = "and " + dList[i] + sTmp
                Parent.SendTwitchMessage(sTmp2)
                Parent.SendDiscordMessage(sTmp2)
                
        lHeisters = []
        lHInput = []

    return

#---------------------------------------
#   [Merchant] Merchant function
#---------------------------------------
def merchant(sMessage): #TO FIN
    global pCurrCustomer

    def menu0(sMessage): #DONE
        global sCurrCustomer
        global pCurrCustomer
        global sPath

        global iArrItems
        global iArrShopItems

        if (sMessage == "1"):
            sTmp = "(Merchant) Great! Welcome to my shop, feel free to browse the items. Just keep in mind that I need to get going in about 5 minutes."
            Parent.SendTwitchWhisper(sCurrCustomer, sTmp)

            iArrShopItems = []
            sTmp = "You see the following items neatly set on the counter: "
            for i in range(0, 5):
                iTmp2 = 1
                if (pCurrCustomer.iPlayerStats[17] != 0):
                    iTmp2 = 1.0 + float(pCurrCustomer.iPlayerStats[17])/100

                while (True):
                    iTmp = rand.randint(0, len(iArrItems)*2 - 1)
                    if (iArrItems[iTmp].iItemTier <= 2):
                        iArrShopItems.append(iArrItems[iTmp])
                        sTmp = sTmp + "[" + str(i+1) + "] " + iArrItems[iTmp].sItemName + " (" + str(int(iTmp2*iArrItems[iTmp].iItemPrice)) + ") - "
                        break

            sTmp = sTmp + " [6] Leave the store"
            iTmp = rand.randint(1, 200)
            if (iTmp <= 75):
                pCurrCustomer.bSecretRoom = True
                sTmp = sTmp + " - [7] You see a secret room, enter it"

            Parent.SendTwitchWhisper(sCurrCustomer, sTmp)

            pCurrCustomer.iMerchMenu = 1

        elif (sMessage == "2"):
            sTmp = " (Merchant) Fine! I didn't want to sell to you in anyway! Now get!"
            Parent.SendTwitchWhisper(sCurrCustomer, sTmp)

            sCurrCustomer = ""
            pCurrCustomer.clear()

        elif (sMessage == "3"):
            sTmp = "Thank you for your input, you will now be removed from the merchant script. If you wish to opt back into the script again please send I_am_steak a DM in discord, he can usually be found at https://discord.gg/xJXtet2 ."
            Parent.SendTwitchWhisper(sCurrCustomer, sTmp)

            sTmp = sPath + "ImeanTechnicallySpeakingifSomeoneHasthisnameontwitchitwouldfuckwiththeprogram.txt"
            fileTmp = open(sTmp, "a")

            fileTmp.write(sCurrCustomer + "\n")

            sCurrCustomer = ""
            pCurrCustomer.clear()

            fileTmp.close()

        else:
            sTmp = "(Merchant) Excuse me? You better stop talking nonsense real fast before I throw you out of here kid."
            Parent.SendTwitchWhisper(sCurrCustomer, sTmp)

        return

    def menu1(sMessage): #DONE
        global sCurrCustomer
        global pCurrCustomer

        global iArrShopItems

        if ((sMessage == "1") or (sMessage == "2") or (sMessage == "3") or (sMessage == "4") or (sMessage == "5")):
            pCurrCustomer.iMerchMenu = 2
            pCurrCustomer.iMerchItem = int(sMessage) - 1

            sTmp = "You pick up " + iArrShopItems[int(sMessage)-1].sItemName + ". Would you like to: [1] Buy " + iArrShopItems[int(sMessage)-1].sItemName + " - [2] Put " + iArrShopItems[int(sMessage)-1].sItemName + " back - [3] Attempt to steal"
            Parent.SendTwitchWhisper(sCurrCustomer, sTmp)

        elif (sMessage == "6"):
            sTmp = "(Merchant) Fine! I didn't want to sell to you in anyway! Now get!"
            Parent.SendTwitchWhisper(sCurrCustomer, sTmp)

            sCurrCustomer = ""
            pCurrCustomer.clear()

        elif (sMessage == "7"):
            if (pCurrCustomer.bSecretRoom == True):
                sTmp = "(Merchant) If I find out you told anyone about my secret room you can consider yourself dead!"
                Parent.SendTwitchWhisper(sCurrCustomer, sTmp)

                sTmp = "The merchant lets you into the secret room and you see the following items: "

                iTmp2 = 1
                if (pCurrCustomer.iPlayerStats[17] != 0):
                    iTmp2 = 1.0 + float(pCurrCustomer.iPlayerStats[17])/100

                for i in range(0, rand.randint(1,4)):
                    while (True):
                        iTmp = rand.randint(0, len(iArrItems)*2 - 1)
                        if (iArrItems[iTmp].iItemTier > 1):
                            iArrShopItems.append(iArrItems[iTmp])
                            sTmp = sTmp + "[" + str(i+1) + "] " + iArrItems[iTmp].sItemName + " (" + str(int(iTmp2*iArrItems[iTmp].iItemPrice)) + ") - "
                            break

                sTmp = sTmp + " [4] Leave the store"
                Parent.SendTwitchWhisper(sCurrCustomer, sTmp)

                pCurrCustomer.iMerchMenu = 4

            else:
                sTmp = "(Merchant) Excuse me? You better stop talking nonsense real fast before I throw you out of here kid."
                Parent.SendTwitchWhisper(sCurrCustomer, sTmp)

        else:
            sTmp = "(Merchant) Excuse me? You better stop talking nonsense real fast before I throw you out of here kid."
            Parent.SendTwitchWhisper(sCurrCustomer, sTmp)

        return

    def menu2(sMessage): #TO FIN
        global sCurrCustomer
        global pCurrCustomer

        global iArrShopItems

        if (sMessage == "1"):
            iTmp2 = 1
            if (pCurrCustomer.iPlayerStats[17] != 0):
                iTmp2 = 1.0 + float(pCurrCustomer.iPlayerStats[17])/100

            sTmp = "Are you sure you would like to purchase " + iArrShopItems[pCurrCustomer.iMerchItem].sItemName + " at a cost of " + str(int(iTmp2*iArrShopItems[pCurrCustomer.iMerchItem].iItemPrice)) + ": [1] yes - [2] no"
            Parent.SendTwitchWhisper(sCurrCustomer, sTmp)

            pCurrCustomer.iMerchMenu = 3

        elif (sMessage == "2"):
            sTmp = "You put " + iArrShopItems[pCurrCustomer.iMerchItem].sItemName + " back on the shelf. The following items are still available: "
            for i in range(0, 5):
                sTmp = sTmp + "[" + str(i+1) + "] " + iArrShopItems[i].sItemName + " (" + str(iArrShopItems[i].iItemPrice) + ") - "

            sTmp = sTmp + "[6] Leave the store"

            if (pCurrCustomer.bSecretRoom == True):
                sTmp = sTmp + " - [7] You see a secret room, enter it"

            Parent.SendTwitchWhisper(sCurrCustomer, sTmp)

            pCurrCustomer.iMerchMenu = 1

        elif (sMessage == "3"):
            sTmp = "You attempt to steal " + iArrShopItems[pCurrCustomer.iMerchItem].sItemName

            iTmp = rand.randint(0, 200)
            if (iTmp <= 10):
                sTmp = sTmp + " successfully and get out of the store as quickly as possible. The merchant will remember your betrayal."
                Parent.SendTwitchWhisper(sCurrCustomer, sTmp)

                for i in range(0, len(pCurrCustomer.iInvSize)):
                    if (pCurrCustomer.itemArrInventory[i] == ""):
                        pCurrCustomer.newInvItem(i, iArrShopItems[pCurrCustomer.imerchItem].sItemName)
                        pCurrCustomer.updatePlayer(sCurrCustomer)

                        sCurrCustomer = ""
                        pCurrCustomer.clear()

                        return

                sTmp = "Unfortunately you don't have space in your inventory to hold the stolen valuables and in the rush to get out without being noticed by the merchant you carelessly drop it."
                Parent.SendTwitchWhisper(sCurrCustomer, sTmp)

            else:
                iTmp = rand.randint(0, 150)
                sTmp = str(iTmp) + " - " + str(float(iTmp)/100) + " - " + str(Parent.GetPoints(sCurrCustomer)) + " - " + str(Parent.GetPoints(sCurrCustomer)*(float(iTmp)/100))
                Parent.RemovePoints(sCurrCustomer, long(Parent.GetPoints(sCurrCustomer)*(float(iTmp)/100)))
                
                sTmp = sTmp + " unsuccessfully and get beaten up by the merchant and his lacky. You lose " + str(iTmp) + "% of your money and now only have " + str(Parent.GetPoints(sCurrCustomer)) + " points left. The merchant will remember your betrayal."
                Parent.SendTwitchWhisper(sCurrCustomer, sTmp)

            sCurrCustomer = ""
            pCurrCustomer.clear()
            endOfMerchantUpdate()

            #TODO add to thief list

        else:
            sTmp = "(Merchant) Excuse me? You better stop talking nonsense real fast before I throw you out of here kid."
            Parent.SendTwitchWhisper(sCurrCustomer, sTmp)

        return

    def menu3(sMessage): #DONE
        global sPath

        global sCurrCustomer
        global pCurrCustomer

        global iArrShopItems

        if (sMessage == "1"):
            if (int(Parent.GetPoints(sCurrCustomer)) >= iArrShopItems[pCurrCustomer.iMerchItem].iItemPrice):
                for i in range(0, pCurrCustomer.iInvSize):
                    if (pCurrCustomer.itemArrInventory[i] == ""):
                        pCurrCustomer.newInvItem(i, iArrShopItems[pCurrCustomer.iMerchItem].sItemName)
                        pCurrCustomer.updatePlayer(sCurrCustomer)

                        iTmp2 = 1
                        if (pCurrCustomer.iPlayerStats[17] != 0):
                            iTmp2 = 1.0 + float(pCurrCustomer.iPlayerStats[17])/100

                        sTmp = "Your purchase the " + iArrShopItems[pCurrCustomer.iMerchItem].sItemName + " at a cost of " + str(int(iTmp2*iArrShopItems[pCurrCustomer.iMerchItem].iItemPrice)) + "."
                        Parent.SendTwitchWhisper(sCurrCustomer, sTmp)

                        Parent.RemovePoints(sCurrCustomer, long(iTmp2*iArrShopItems[pCurrCustomer.iMerchItem].iItemPrice))

                        sTmp = "(Merchant) Thanks for the purchase kid! Be seeing you around."
                        Parent.SendTwitchWhisper(sCurrCustomer, sTmp)

                        sCurrCustomer = ""
                        pCurrCustomer.clear()
                        endOfMerchantUpdate()

                        return

                sTmp = "Unfortunately you don't have space in your inventory to hold a new item"
                Parent.SendTwitchWhisper(sCurrCustomer, sTmp)

                sTmp = "(Merchant) You can't even carry the things you want to buy from me? Haha, stop wasting my time kiddo"
                Parent.SendTwitchWhisper(sCurrCustomer, sTmp)

            else:
                sTmp = "You don't currently have enough money to buy this item!"
                Parent.SendTwitchWhisper(sCurrCustomer, sTmp)
                sTmp = "(Merchant) You ain't got no money? What a waste of my time."
                Parent.SendTwitchWhisper(sCurrCustomer, sTmp)

            sCurrCustomer = ""
            pCurrCustomer.clear()

        elif (sMessage == "2"):
            sTmp = "You put " + iArrShopItems[pCurrCustomer.iMerchItem].sItemName + " back on the shelf. The following items are still available: "
            for i in range(0, 5):
                sTmp = sTmp + "[" + str(i+1) + "] " + iArrShopItems[i].sItemName + " (" + str(iArrShopItems[i].iItemPrice) + ") - "

            sTmp = sTmp + "[6] Leave the store"

            if (pCurrCustomer.bSecretRoom == True):
                sTmp = sTmp + " - [7] You see a secret room, enter it"

            Parent.SendTwitchWhisper(sCurrCustomer, sTmp)

            pCurrCustomer.iMerchMenu = 1

        else:
            sTmp = "(Merchant) Excuse me? You better stop talking nonsense real fast before I throw you out of here kid."
            Parent.SendTwitchWhisper(sCurrCustomer, sTmp)

        return

    def menu4(sMessage): #DONE
        global sCurrCustomer
        global pCurrCustomer

        global iArrShopItems

        if ((sMessage == "1") or (sMessage == "2") or (sMessage == "3")):
            try:
                pCurrCustomer.iMerchMenu = 5
                pCurrCustomer.iMerchItem = int(sMessage) + 4

                sTmp = "You pick up " + iArrShopItems[int(sMessage) + 4].sItemName + ". Would you like to: [1] Buy " + iArrShopItems[int(sMessage) + 4].sItemName + " - [2] Put " + iArrShopItems[int(sMessage) + 4].sItemName + " back - [3] Attempt to steal"
                Parent.SendTwitchWhisper(sCurrCustomer, sTmp)
            except:
                pCurrCustomer.iMerchMenu = 4
                pCurrCustomer.imerchItem = -1

                sTmp = "(Merchant) Sorry, I can't let you see that item. I'm saving it for... a special occasion"
                Parent.SendTwitchWhisper(sCurrCustomer, sTmp)

        elif (sMessage == "4"):
            sTmp = "(Merchant) Remember! Anyone finds out you were in here, and you're dead. Now get out of my store!"
            Parent.SendTwitchWhisper(sCurrCustomer, sTmp)

            sCurrCustomer = ""
            pCurrCustomer.clear()

        else:
            sTmp = "(Merchant) Excuse me? You better stop talking nonsense real fast before I throw you out of here kid."
            Parent.SendTwitchWhisper(sCurrCustomer, sTmp)

        return

    def menu5(sMessage): #TO FIN
        global sCurrCustomer
        global pCurrCustomer

        global iArrShopItems

        if (sMessage == "1"):
            iTmp2 = 1
            if (pCurrCustomer.iPlayerStats[17] != 0):
                iTmp2 = 1.0 + float(pCurrCustomer.iPlayerStats[17])/100

            sTmp = "Are you sure you would like to purchase " + iArrShopItems[pCurrCustomer.iMerchItem].sItemName + " at a cost of " + str(int(iTmp2*iArrShopItems[pCurrCustomer.iMerchItem].iItemPrice)) + ": [1] yes - [2] no" 
            Parent.SendTwitchWhisper(sCurrCustomer, sTmp)

            pCurrCustomer.iMerchMenu = 6

        elif (sMessage == "2"):
            sTmp = "You put " + iArrShopItems[pCurrCustomer.iMerchItem].sItemName + " back on the shelf. The following items are still available: "
            for i in range(5, len(iArrShopItems)):
                sTmp = sTmp + "[" + str(i-4) + "] " + iArrShopItems[i].sItemName + " (" + str(iArrShopItems[i].iItemPrice) + ") - "

            sTmp = sTmp + "[4] Leave the store"
            Parent.SendTwitchWhisper(sCurrCustomer, sTmp)

            pCurrCustomer.iMerchMenu = 4

        elif (sMessage == "3"):
            iTmp = rand.randint(50, 200)
            Parent.RemovePoints(sCurrCustomer, Parent.GetPoints(sCurrCustomer)*(float(iTmp)/10))

            sTmp = "You attempt to steal " + str(pCurrCustomer.iMerchItem) + " unsuccessfully and get beaten up by the merchant and his lacky. You lose " + str(iTmp) + "% of your money and now only have $check amount$ left. The merchant will remember your betrayal."
            Parent.SendTwitchWhisper(sCurrCustomer, sTmp)


            sCurrCustomer = ""
            pCurrCustomer.clear()
            endOfMerchantUpdate()

            #TODO add to thief list
        else:
            sTmp = "(Merchant) Excuse me? You better stop talking nonsense real fast before I throw you out of here kid."
            Parent.SendTwitchWhisper(sCurrCustomer, sTmp)

        return

    def menu6(sMessage): #DONE
        global sPath

        global sCurrCustomer
        global pCurrCustomer

        if (sMessage == "1"):
            if (int(Parent.GetPoints(sCurrCustomer)) >= iArrShopItems[pCurrCustomer.iMerchItem].iItemPrice):
                for i in range(0, pCurrCustomer.iInvSize):
                    if (pCurrCustomer.itemArrInventory[i] == ""):
                        pCurrCustomer.newInvItem(i, iArrShopItems[pCurrCustomer.iMerchItem].sItemName)
                        pCurrCustomer.updatePlayer(sCurrCustomer)

                        iTmp2 = 1
                        if (pCurrCustomer.iPlayerStats[17] != 0):
                            iTmp2 = 1.0 + float(pCurrCustomer.iPlayerStats[17])/100

                        sTmp = "Your purchase the " + iArrShopItems[pCurrCustomer.iMerchItem].sItemName + " at a cost of " + str(int(iTmp2*iArrShopItems[pCurrCustomer.iMerchItem].iItemPrice)) + "."
                        Parent.SendTwitchWhisper(sCurrCustomer, sTmp)

                        Parent.RemovePoints(sCurrCustomer, long(iTmp2*iArrShopItems[pCurrCustomer.iMerchItem].iItemPrice))

                        sTmp = "(Merchant) Thanks for the purchase kid! Be seeing you around."
                        Parent.SendTwitchWhisper(sCurrCustomer, sTmp)

                        sCurrCustomer = ""
                        pCurrCustomer.clear()
                        endOfMerchantUpdate()

                        return

                sTmp = "Unfortunately you don't have space in your inventory to hold a new item"
                Parent.SendTwitchWhisper(sCurrCustomer, sTmp)

                sTmp = "(Merchant) You can't even carry the things you want to buy from me? Haha, stop wasting my time kiddo"
                Parent.SendTwitchWhisper(sCurrCustomer, sTmp)

            else:
                sTmp = "You don't currently have enough money to buy this item!"
                Parent.SendTwitchWhisper(sCurrCustomer, sTmp)
                sTmp = "(Merchant) You ain't got no money? What a waste of my time."
                Parent.SendTwitchWhisper(sCurrCustomer, sTmp)

            sCurrCustomer = ""
            pCurrCustomer.clear()

        elif (sMessage == "2"):
            sTmp = "You put " + iArrShopItems[pCurrCustomer.iMerchItem].sItemName + " back on the shelf. The following items are still available: "
            for i in range(5, len(iArrShopItems)):
                sTmp = sTmp + "[" + str(i-4) + "] " + iArrShopItems[i].sItemName + " (" + str(iArrShopItems[i].iItemPrice) + ") - "

            sTmp = sTmp + "[4] Leave the store"
            Parent.SendTwitchWhisper(sCurrCustomer, sTmp)

            pCurrCustomer.iMerchMenu = 4

        else:
            sTmp = "(Merchant) Excuse me? You better stop talking nonsense real fast before I throw you out of here kid."
            Parent.SendTwitchWhisper(sCurrCustomer, sTmp)

        return

    menuOptions = {
        0: menu0,
        1: menu1,
        2: menu2,
        3: menu3, 
        4: menu4,
        5: menu5,
        6: menu6
    }

    menuOptions[pCurrCustomer.iMerchMenu](sMessage)

    return

def endOfMerchantUpdate():
    global sPath
    global sCurrCustomer

    global arrSInventory
    global arrPInventory

    if (sCurrCustomer in arrSInventory):
        tmpCustard = arrPInventory[arrSInventory.index(sCurrCustomer)]
        tmpCustard.refreshPlayer(sCurrCustomer, sPath)

    return
#---------------------------------------
#   [Inventory] Inventory Function
#---------------------------------------
def inventory(sMessage, sUser): #DONE
    global sPath

    global arrPInventory
    global arrSInventory

    if (sUser not in arrSInventory):
        newCustomer = Player()
        newCustomer.refreshPlayer(sUser, sPath)
        newCustomer.iInvMenu = 0

        arrPInventory.append(newCustomer)
        arrSInventory.append(sUser)


    tmpCustard = arrPInventory[arrSInventory.index(sUser)]
    playerInventory(sMessage, sUser, tmpCustard)

    return

def playerInventory(sMessage, sUser, pCustomer): #DONE ???
    global iArrItems
    global sPath

    if (pCustomer.iInvMenu == 0): # DONE - start
        sTmp = "(Inventory Manager) Hi! Would you like to browse your inventory? [1] yes - [2] no"
        Parent.SendTwitchWhisper(sUser, sTmp)

        pCustomer.iInvMenu = 1

    elif (pCustomer.iInvMenu == 1): # DONE - initial
        if (sMessage == "1"):
            playerWearingOut(sUser, pCustomer)

            pCustomer.iInvMenu = 2

        else:
            sTmp = "(Inventory Manager) Alright then! Have a good day!"
            Parent.SendTwitchWhisper(sUser, sTmp)

            pCustomer.iInvMenu = 0

    elif (pCustomer.iInvMenu == 2): # DONE - items
        try:
            iTmp = int(sMessage)

            if ((iTmp >= 1) and (iTmp <= 5)):
                if (pCustomer.itemArrEquipped[iTmp-1] != ""):
                    sTmp = "You consider " + pCustomer.itemArrEquipped[iTmp-1] + ", would you like to: [1] unequip - [2] sell - [3] inspect"
                    Parent.SendTwitchWhisper(sUser, sTmp)

                    pCustomer.iInvMenu = 3
                    pCustomer.iInvItem = iTmp-1
                else:
                    sTmp = "(Inventory Manager) You don't currently have an item equipped in that slot."
                    Parent.SendTwitchWhisper(sUser, sTmp)

            elif (iTmp <= 12):
                if (pCustomer.itemArrInventory[iTmp-6] != ""):
                    sTmp = "You consider " + pCustomer.itemArrInventory[iTmp-6] + ", would you like to: [1] equip - [2] sell - [3] inspect"
                    Parent.SendTwitchWhisper(sUser, sTmp)

                    pCustomer.iInvMenu = 6
                    pCustomer.iInvItem = iTmp-6
                else:
                    sTmp = "(Inventory Manager) You don't currently have an item in that inventory slot."
                    Parent.SendTwitchWhisper(sUser, sTmp)

        except Exception as e:
            sTmp = "(Inventory Manager) Sorry, the option you have chosen is invalid. Please try again"
            Parent.SendTwitchWhisper(sUser, sTmp)
            Parent.SendTwitchMessage(e.message)

    elif (pCustomer.iInvMenu == 3): # DONE - unequip, sell, inspect
        if (sMessage == "1"):
            for i in range(0, pCustomer.iInvSize):
                if (pCustomer.itemArrInventory[i] == ""):
                    sTmp = "(Inventory Manager) Are you sure you want to unequip " + pCustomer.itemArrEquipped[pCustomer.iInvItem] + "? [1] yes - [2] no"
                    Parent.SendTwitchWhisper(sUser, sTmp)

                    pCustomer.iInvMenu = 4
                    return

            sTmp = "(Inventory Manager) There is currently no space in your inventory to move " + pCustomer.itemArrEquipped[pCustomer.iInvItem] + " to."
            Parent.SendTwitchWhisper(sUser, sTmp)

            sTMp = "(Inventory Manager) Would you like to continue managing your inventory? [1] yes - [2] no"
            Parent.SendTwitchWhisper(sUser, sTmp)

            pCustomer.iInvMenu = 1
            pCustomer.iInvItem = -1

        elif (sMessage == "2"):
            global iArrItems

            sTmp = pCustomer.itemArrEquipped[pCustomer.iInvItem]
            iTmp = 0
            for i in range(0, len(iArrItems)):
                if (iArrItems[i].sItemName == sTmp):
                    iTmp = iArrItems[i].iItemPrice/4                                                                    #PROCESSING HIGH: store this value instead of recalculating in menu 5
            sTmp = "(Inventory Manager) Are you sure you would like to sell " + pCustomer.itemArrEquipped[pCustomer.iInvItem] + " for " + str(iTmp) + " TiltCoin? [1] yes - [2] no"
            Parent.SendTwitchWhisper(sUser, sTmp)

            pCustomer.iInvMenu = 5

        elif (sMessage == "3"):
            for i in range(0, len(iArrItems)):
                if (iArrItems[i].sItemName == pCustomer.itemArrEquipped[pCustomer.iInvItem]):
                    whisperItemStats(sUser, iArrItems[i])

                    sTmp = "(Inventory Manager) Would you like to continue managing your inventory? [1] yes - [2] no"
                    Parent.SendTwitchWhisper(sUser, sTmp)

                    pCustomer.iInvMenu = 1
                    pCustomer.iInvItem = -1

                    return
                    
            sTmp = "An error occured, would you ever so kindly whisper I_am_steak a message with \"Error: frogosaurus D:\" thank you"
            Parent.SendTwitchWhisper(sUser, sTmp)

        else:
            sTmp = "(Inventory Manager) Sorry, the option you have chosen is invalid. Please try again"
            Parent.SendTwitchWhisper(sUser, sTmp)

    elif (pCustomer.iInvMenu == 4): # DONE - unequip
        if (sMessage == "1"):
            for i in range(0, pCustomer.iInvSize):
                if (pCustomer.itemArrInventory[i] == ""):
                    for j in range(0, len(iArrItems)):
                        if (iArrItems[j].sItemName == pCustomer.itemArrEquipped[pCustomer.iInvItem]):
                            pCustomer.removeItemStats(iArrItems[j])
                            pCustomer.swapItems(pCustomer.iInvItem, i)
                            pCustomer.updatePlayer(sUser)

                            sTmp = "(Inventory Manager) You have successfully unequipped " + pCustomer.itemArrInventory[i] + "."
                            Parent.SendTwitchWhisper(sUser, sTmp)

                            sTmp = "(Inventory Manager) Would you like to continue managing your inventory? [1] yes - [2] no"
                            Parent.SendTwitchWhisper(sUser, sTmp)

                            pCustomer.iInvMenu = 1
                            pCustomer.iInvItem = -1

                            return

                    sTmp = "AN error occured, please whisper i_am_steak with the message \"Error: Staying Alive\" k thanks bye"
                    Parent.SendTwitchWhisper(sUser, sTmp)

                    sTMp = "(Inventory Manager) Would you like to continue managing your inventory? [1] yes - [2] no"
                    Parent.SendTwitchWhisper(sUser, sTmp)

                    pCustomer.iInvMenu = 1
                    pCustomer.iInvItem = -1

                    return

            sTmp = "An error occured unequpping the item, please send i_am_steak a message with ''Error Butterfingers'' k thanks bye"
            Parent.SendTwitchWhisper(sUser, sTmp)


            sTMp = "(Inventory Manager) Would you like to continue managing your inventory? [1] yes - [2] no"
            Parent.SendTwitchWhisper(sUser, sTmp)

            pCustomer.iInvMenu = 1
            pCustomer.iInvItem = -1

        elif (sMessage == "2"):
            playerWearingOut(sUser, pCustomer)

            pCustomer.iInvMenu = 2
            pCustomer.iInvItem = -1

        else:
            sTmp = "(Inventory Manager) Sorry, the option you have chosen is invalid. Please try again"
            Parent.SendTwitchWhisper(sUser, sTmp)

    elif (pCustomer.iInvMenu == 5): # DONE - sell
        if (sMessage == "1"):
            sTmp = pCustomer.itemArrEquipped[pCustomer.iInvItem]
            iTmp = 0
            for i in range(0, len(iArrItems)):
                if (iArrItems[i].sItemName == sTmp):
                    iTmp = iArrItems[i].iItemPrice/4  

                    pCustomer.deleteEqpItem(pCustomer.iInvItem)
                    pCustomer.removeItemStats(iArrItems[i])
                    pCustomer.updatePlayer(sUser)

                    Parent.AddPoints(sUser, long(iTmp))

                    sTmp = "(Inventory Manager) You sold " + pCustomer.itemArrEquipped[pCustomer.iInvItem] + " for " + str(iTmp) + ". You now have " +str(Parent.GetPoints(sUser)) + " TiltCoin."
                    Parent.SendTwitchWhisper(sUser, sTmp)

                    sTmp = "(Inventory Manager) Would you like to continue managing your inventory? [1] yes - [2] no"
                    Parent.SendTwitchWhisper(sUser, sTmp)

                    pCustomer.iInvMenu = 1
                    pCustomer.iInvItem = -1

                    return

            sTmp = "Ooops, we had a little accident ^^ please whisper i_am_steak with \"Error DESTINY\" thank you ^^"
            Parent.SendTwitchWhisper(sUser, sTmp)

            sTmp = "(Inventory Manager) Would you like to continue managing your inventory? [1] yes - [2] no"
            Parent.SendTwitchWhisper(sUser, sTmp)

            pCustomer.iInvMenu = 1
            pCustomer.iInvItem = -1

        elif (sMessage == "2"):
            playerWearingOut(sUser, pCustomer)

            pCustomer.iInvMenu = 2
            pCustomer.iInvItem = -1

        else:
            sTmp = "(Inventory Manager) Sorry, the option you have chosen is invalid. Please try again"
            Parent.SendTwitchWhisper(sUser, sTmp)

    elif (pCustomer.iInvMenu == 6): # DONE - equip, sell, inspect
        if (sMessage == "1"):
            for i in range(0, len(iArrItems)):
                if (iArrItems[i].sItemName == pCustomer.itemArrInventory[pCustomer.iInvItem]):
                    if (pCustomer.itemArrEquipped[iArrItems[i].iItemPosition] != ""):
                        sTmp = "(Inventory Manager) Are you sure you would like to swap out " + pCustomer.itemArrEquipped[iArrItems[i].iItemPosition] + " for " + pCustomer.itemArrInventory[pCustomer.iInvItem] + "? [1] yes - [2] no"
                        Parent.SendTwitchWhisper(sUser, sTmp)

                    else:
                        sTmp = "(Inventory Manager) Are you sure you would like to equip " + pCustomer.itemArrInventory[pCustomer.iInvItem] + "? [1] yes - [2] no"
                        Parent.SendTwitchWhisper(sUser, sTmp)

                    pCustomer.iInvMenu = 7

                    return

            Parent.SendTwitchWhisper(suser, "Shit went wrong fam")

        elif (sMessage == "2"): 
            sTmp = pCustomer.itemArrInventory[pCustomer.iInvItem]
            iTmp = 0
            for i in range(0, len(iArrItems)):
                if (iArrItems[i].sItemName == sTmp):
                    iTmp = iArrItems[i].iItemPrice/4  

                    sTmp = "(Inventory Manager) Are you sure you would like to sell " + pCustomer.itemArrInventory[pCustomer.iInvItem] + " for " + str(iTmp) + "? [1] yes - [2] no"
                    Parent.SendTwitchWhisper(sUser, sTmp)

                    pCustomer.iInvMenu = 8

                    return

            sTmp = "Oh no I made an oopsie VoHiYo please whisper i_am_steak with \"Error: magnet lord D:\" thank you VoHiYo"
            Parent.SendTwitchWhisper(sUser, sTmp)

            sTmp = "(Inventory Manager) Would you like to continue managing your inventory? [1] yes - [2] no"
            Parent.SendTwitchWhisper(sUser, sTmp)

            pCustomer.iInvMenu = 1
            pCustomer.iInvItem = -1

        elif (sMessage == "3"):
            for i in range(0, len(iArrItems)):
                if (iArrItems[i].sItemName == pCustomer.itemArrInventory[pCustomer.iInvItem]):
                    whisperItemStats(sUser, iArrItems[i])

                    sTmp = "(Inventory Manager) Would you like to continue managing your inventory? [1] yes - [2] no"
                    Parent.SendTwitchWhisper(sUser, sTmp)

                    pCustomer.iInvMenu = 1
                    pCustomer.iInvItem = -1

                    return

            sTmp = "An error occured, would you ever so kindly whisper I_am_steak a message with \"Error: and if its quite alright, I need you baby\" thank you"
            Parent.SendTwitchWhisper(sUser, sTmp)

        else:
            sTmp = "(Inventory Manager) Sorry, the option you have chosen is invalid. Please try again"
            Parent.SendTwitchWhisper(sUser, sTmp)

    elif (pCustomer.iInvMenu == 7): # DONE - equip
        if (sMessage == "1"):
            for i in range(0, len(iArrItems)):
                if (iArrItems[i].sItemName == pCustomer.itemArrInventory[pCustomer.iInvItem]):
                    iTmp = iArrItems[i].iItemPosition

                    if (pCustomer.itemArrEquipped[iTmp] != ""):
                        for j in range(0, len(iArrItems)):
                            if (iArrItems[j].sItemName == pCustomer.itemArrEquipped[iTmp]):
                                pCustomer.removeItemStats(iArrItems[j])
                    
                    pCustomer.swapItems(iTmp, pCustomer.iInvItem)
                    pCustomer.addItemStats(iArrItems[i])
                    pCustomer.updatePlayer(sUser)

                    sTmp = "(Inventory Manager) You have successfully equipped " + pCustomer.itemArrEquipped[iTmp] + "."
                    Parent.SendTwitchWhisper(sUser, sTmp)

                    sTmp = "(Inventory Manager) Would you like to continue managing your inventory? [1] yes - [2] no"
                    Parent.SendTwitchWhisper(sUser, sTmp)

                    pCustomer.iInvMenu = 1
                    pCustomer.iInvItem = -1

                    return

            sTmp = "Ooops, we had a little accident ^^ please whisper i_am_steak with \"Error WOOOOOOOOOOWeeeee\" thank you ^^"
            Parent.SendTwitchWhisper(sUser, sTmp)

            sTMp = "(Inventory Manager) Would you like to continue managing your inventory? [1] yes - [2] no"
            Parent.SendTwitchWhisper(sUser, sTmp)

            pCustomer.iInvMenu = 1
            pCustomer.iInvItem = -1

        elif (sMessage == "2"):
            playerWearingOut(sUser, pCustomer)

            pCustomer.iInvMenu = 2
            pCustomer.iInvItem = -1

        else:
            sTmp = "(Inventory Manager) Sorry, the option you have chosen is invalid. Please try again"
            Parent.SendTwitchWhisper(sUser, sTmp)

    elif (pCustomer.iInvMenu == 8): # DONE - sell
        if (sMessage == "1"):
            sTmp = pCustomer.itemArrInventory[pCustomer.iInvItem]
            iTmp = 0
            for i in range(0, len(iArrItems)):
                if (iArrItems[i].sItemName == sTmp):
                    iTmp = iArrItems[i].iItemPrice/4  

                    Parent.deleteInvItem(pCustomer.iInvItem)
                    Parent.updatePlayer(sUser)
                    Parent.AddPoints(sUser, long(iTmp))

                    sTmp = "(Inventory Manager) You sold " + pCustomer.itemArrInventory[pCustomer.iInvItem] + " for " + str(iTmp) + ". You now have " +str(Parent.GetPoints(sUser)) + " TiltCoin."
                    Parent.SendTwitchWhisper(sUser, stmp)

                    sTMp = "(Inventory Manager) Would you like to continue managing your inventory? [1] yes - [2] no"
                    Parent.SendTwitchWhisper(sUser, sTmp)

                    pCustomer.iInvMenu = 1
                    pCustomer.iInvItem = -1

                    return

            sTmp = "Ooops, we had a little accident ^^ please whisper i_am_steak with \"Error WOOOOOOOOOOWeeeee\" thank you ^^"
            Parent.SendTwitchWhisper(sUser, sTmp)


        elif (sMessage == "2"):
            playerWearingOut(sUser, pCustomer)

            pCustomer.iInvMenu = 2
            pCustomer.iInvItem = -1

        else:
            sTmp = "(Inventory Manager) Sorry, the option you have chosen is invalid. Please try again"
            Parent.SendTwitchWhisper(sUser, sTmp)

    else:
        sTmp = "Ummm, this is gna sound a bit weird but could you whisper i_am_steak with \"Error: mega death inbox\" thanks k bye <3"
        Parent.SendTwitchWhisper(sUser, sTmp)

    return

def playerWearingOut(sUser, pCustomer): #DONE ???
    sTmp = "You are currently wearing the following: [1] "
    if (pCustomer.itemArrEquipped[0] == ""):
        sTmp = sTmp + "<None> (head) - [2] "
    else:
        sTmp = sTmp + pCustomer.itemArrEquipped[0] + " (head) - [2] "

    if (pCustomer.itemArrEquipped[1] == ""):
        sTmp = sTmp + "<None> (upper body) - [3] "
    else:
        sTmp = sTmp + pCustomer.itemArrEquipped[1] + " (upper body) - [3] "

    if (pCustomer.itemArrEquipped[2] == ""):
        sTmp = sTmp + "<None> (lower body) - [4] "
    else:
        sTmp = sTmp + pCustomer.itemArrEquipped[2] + " (lower body) - [4] "

    if (pCustomer.itemArrEquipped[3] == ""):
        sTmp = sTmp + "<None> (feet) - [5] "
    else:
        sTmp = sTmp + pCustomer.itemArrEquipped[3] + " (feet) - [5] "

    if (pCustomer.itemArrEquipped[4] == ""):
        sTmp = sTmp + "<None> (weapon) - "
    else:
        sTmp = sTmp + pCustomer.itemArrEquipped[4] + " (weapon) - "

    Parent.SendTwitchWhisper(sUser, sTmp)

    sTmp = "You have the following items in your inventory: "
    for i in range(0, pCustomer.iInvSize):
        if(pCustomer.itemArrInventory[i] == ""):
            sTmp = sTmp + "[" + str(i+6) + "] <None> - "
        else:
            sTmp = sTmp + "[" + str(i+6) + "] " + pCustomer.itemArrInventory[i] + " - "

    sTmp = sTmp[:len(sTmp)-2]

    Parent.SendTwitchWhisper(sUser, sTmp)

def whisperItemStats(sUser, iTmpItem): #TODO
    sTmp = "(Item Manager) You inspect " + iTmpItem.sItemName + ", it has the following stats: " 
    fTmp = False

    if (iTmpItem.iItemAttributes[0] != 0):
        fTmp = True

        if (iTmpItem.iItemAttributes[0] > 0):
            sTmp = sTmp + str(iTmpItem.iItemAttributes[0]) + "% increased death chance (heist)"
        else:
            sTmp = sTmp + str(-1*iTmpItem.iItemAttributes[0]) + "% decreased death chance (heist)"

    if (iTmpItem.iItemAttributes[1] != 0):
        if (fTmp == True):
            sTmp = sTmp + ", "
        else:
            fTmp = True

        if (iTmpItem.iItemAttributes[1] > 0):
            sTmp = sTmp + str(iTmpItem.iItemAttributes[1]) + "% increased payout (heist)"
        else:
            sTmp = sTmp + str(-1*iTmpItem.iItemAttributes[1]) + "% decreased payout (heist)"

    if (iTmpItem.iItemAttributes[2] != 0):
        if (fTmp == True):
            sTmp = sTmp + ", "
        else:
            fTmp = True

        if (iTmpItem.iItemAttributes[2] > 0):
            sTmp = sTmp + str(iTmpItem.iItemAttributes[2]) + " incresed payout on win (heist)"
        else:
            sTmp = sTmp + str(-1*iTmpItem.iItemAttributes[2]) + " decreased payout on win (heist)"

    if (iTmpItem.iItemAttributes[3] != 0):
        if (fTmp == True):
            sTmp = sTmp + ", "
        else:
            fTmp = True

        if (iTmpItem.iItemAttributes[3] > 0):
            sTmp = sTmp + str(iTmpItem.iItemAttributes[3]) + " increased payout (heist)"
        else:
            sTmp = sTmp + str(-1*iTmpItem.iItemAttributes[3]) + " decreased payout (heist)"

    if (iTmpItem.iItemAttributes[4] != 0):
        if (fTmp == True):
            sTmp = sTmp + ", "
        else:
            fTmp = True

        if (iTmpItem.iItemAttributes[4] > 0):
            sTmp = sTmp + str(iTmpItem.iItemAttributes[4]) + "% increased team death chance (heist)"
        else:
            sTmp = sTmp + str(-1*iTmpItem.iItemAttributes[4]) + "% decreased team death chance (heist)"

    if (iTmpItem.iItemAttributes[5] != 0):
        if (fTmp == True):
            sTmp = sTmp + ", "
        else:
            fTmp = True

        if (iTmpItem.iItemAttributes[5] > 0):
            sTmp = sTmp + str(iTmpItem.iItemAttributes[5]) + "% increased team payout (heist)"
        else:
            sTmp = sTmp + str(-1*iTmpItem.iItemAttributes[5]) + "% decreased team payout (heist)"

    if (iTmpItem.iItemAttributes[6] != 0):
        if (fTmp == True):
            sTmp = sTmp + ", "
        else:
            fTmp = True

        if (iTmpItem.iItemAttributes[6] > 0):
            sTmp = sTmp + str(iTmpItem.iItemAttributes[6]) + " increased team payout on win (heist)"
        else:
            sTmp = sTmp + str(-1*iTmpItem.iItemAttributes[6]) + " decreased team payout on win (heist)"

    if (iTmpItem.iItemAttributes[7] != 0):
        if (fTmp == True):
            sTmp = sTmp + ", "
        else:
            fTmp = True

        if (iTmpItem.iItemAttributes[7] > 0):
            sTmp = sTmp + str(iTmpItem.iItemAttributes[7]) + " increased team payout (heist)"
        else:
            sTmp = sTmp + str(-1*iTmpItem.iItemAttributes[7]) + " decreased team payout (heist)"

    if (iTmpItem.iItemAttributes[8] != 0):
        if (fTmp == True):
            sTmp = sTmp + ", "
        else:
            fTmp = True

        if (iTmpItem.iItemAttributes[8] > 0):
            sTmp = sTmp + str(iTmpItem.iItemAttributes[8]) + "% increased death chance (1v1)"
        else:
            sTmp = sTmp + str(-1*iTmpItem.iItemAttributes[8]) + "% decreased death chance (1v1)"

    if (iTmpItem.iItemAttributes[9] != 0):
        if (fTmp == True):
            sTmp = sTmp + ", "
        else:
            fTmp = True

        if (iTmpItem.iItemAttributes[9] > 0):
            sTmp = sTmp + str(iTmpItem.iItemAttributes[9]) + "% increased payout (1v1)"
        else:
            sTmp = sTmp + str(-1*iTmpItem.iItemAttributes[9]) + "% decreased payout (1v1)"

    if (iTmpItem.iItemAttributes[10] != 0):
        if (fTmp == True):
            sTmp = sTmp + ", "
        else:
            fTmp = True

        if (iTmpItem.iItemAttributes[10] > 0):
            sTmp = sTmp + str(iTmpItem.iItemAttributes[10]) + " increased payout on win (1v1)"
        else:
            sTmp = sTmp + str(-1*iTmpItem.iItemAttributes[10]) + " decreased payout on win (1v1)"

    if (iTmpItem.iItemAttributes[11] != 0):
        if (fTmp == True):
            sTmp = sTmp + ", "
        else:
            fTmp = True

        if (iTmpItem.iItemAttributes[11] > 0):
            sTmp = sTmp + str(iTmpItem.iItemAttributes[11]) + " increased payout (1v1)"
        else:
            sTmp = sTmp + str(-1*iTmpItem.iItemAttributes[11]) + " decreased payout (1v1)"

    if (iTmpItem.iItemAttributes[12] != 0):
        if (fTmp == True):
            sTmp = sTmp + ", "
        else:
            fTmp = True

        sTmp = sTmp + str(iTmpItem.iItemAttributes[12]) + "% chance to recover 20% of money on death (heist, 1v1)"

    if (iTmpItem.iItemAttributes[13] != 0):
        if (fTmp == True):
            sTmp = sTmp + ", "
        else:
            fTmp = True

        sTmp = sTmp + "recover " +  str(iTmpItem.iItemAttributes[13]) + "% of money on death (heist, 1v1)"

    if (iTmpItem.iItemAttributes[14] != 0):
        if (fTmp == True):
            sTmp = sTmp + ", "
        else:
            fTmp = True

        sTmp = sTmp + str(iTmpItem.iItemAttributes[14]) + " payout for first chat message (heist)"

    if (iTmpItem.iItemAttributes[15] != 0):
        if (fTmp == True):
            sTmp = sTmp + ", "
        else:
            fTmp = True

        sTmp = sTmp + str(iTmpItem.iItemAttributes[15]) + "% chance to get +2 points on chat msg"

    if (iTmpItem.iItemAttributes[16] != 0):
        if (fTmp == True):
            sTmp = sTmp + ", "
        else:
            fTmp = True

        if (iTmpItem.iItemAttributes[16] > 0):
            sTmp = sTmp + str(iTmpItem.iItemAttributes[16]) + " points on chat message"
        else:
            sTmp = sTmp + "-" + str(-1*iTmpItem.iItemAttributes[16]) + " points on chat message"

    if (iTmpItem.iItemAttributes[17] != 0):
        if (fTmp == True):
            sTmp = sTmp + ", "
        else:
            fTmp = True

        if (iTmpItem.iItemAttributes[17] > 0):
            sTmp = sTmp + str(iTmpItem.iItemAttributes[17]) + "% increased item cost"
        else:
            sTmp = sTmp + str(-1*iTmpItem.iItemAttributes[17]) + "% decreased item cost"

    if (iTmpItem.iItemAttributes[18] != 0):
        if (fTmp == True):
            sTmp = sTmp + ", "
        else:
            fTmp = True

        if (iTmpItem.iItemAttributes[18] > 0):
            sTmp = sTmp + str(iTmpItem.iItemAttributes[18]) + "% increased chance to find secret room"
        else:
            sTmp = sTmp + str(-1*iTmpItem.iItemAttributes[18]) + "% decreased chance to find secret room"

    if (iTmpItem.iItemAttributes[19] != 0):
        if (fTmp == True):
            sTmp = sTmp + ", "
        else:
            fTmp = True

        if (iTmpItem.iItemAttributes[19] > 0):
            sTmp = sTmp + str(iTmpItem.iItemAttributes[19]) + " extra item/s in secret room"
        else:
            sTmp = sTmp + str(-1*iTmpItem.iItemAttributes[19]) + " less item/s in secret room"

    if (iTmpItem.iItemAttributes[20] != 0):
        if (fTmp == True):
            sTmp = sTmp + ", "
        else:
            fTmp = True

        if (iTmpItem.iItemAttributes[20] > 0):
            sTmp = sTmp + str(iTmpItem.iItemAttributes[20]) + "% increased chance of successfull theft"
        else:
            sTmp = sTmp + str(-1*iTmpItem.iItemAttributes[20]) + "% decreased chance of successfull theft"

    if (iTmpItem.iItemAttributes[21] != 0):
        if (fTmp == True):
            sTmp = sTmp + ", "
        else:
            fTmp = True

        if (iTmpItem.iItemAttributes[21] > 0):
            sTmp = sTmp + str(iTmpItem.iItemAttributes[21]) + "% increased damage on theft"
        else:
            sTmp = sTmp + str(-1*iTmpItem.iItemAttributes[21]) + "% decreased damage on theft"

    if (iTmpItem.iItemAttributes[22] != 0):
        if (fTmp == True):
            sTmp = sTmp + ", "
        else:
            fTmp = True

        if (iTmpItem.iItemAttributes[22] > 0):
            sTmp = sTmp + str(iTmpItem.iItemAttributes[22]) + " more day/s on thievery list"
        else:
            sTmp = sTmp + str(-1*iTmpItem.iItemAttributes[22]) + " less day/s on thievery list"

    sTmp = sTmp + ". Position: "
    if (iTmpItem.iItemPosition == 0):
        sTmp = sTmp + "head - "
    elif (iTmpItem.iItemPosition == 1):
        sTmp = sTmp + "upper body - "
    elif (iTmpItem.iItemPosition == 2):
        sTmp = sTmp + "lower body - "
    elif (iTmpItem.iItemPosition == 3):
        sTmp = sTmp + "feet - "
    else:
        sTmp = sTmp + "weapon - "

    sTmp = sTmp + "Tier: " + str(iTmpItem.iItemTier) + " - Description: " + iTmpItem.sItemDescription

    Parent.SendTwitchWhisper(sUser, sTmp)
    return

#---------------------------------------
#   [Other]
#---------------------------------------