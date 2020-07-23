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
ScriptName = "backend script"
Website = "https://github.com/SteanKotze/curly-octo-funicular"
Creator = "I_am_steak"
Version = "0.1"
Description = "This script are do many heist (/O.O)/"

#---------------------------------------
#   Set Variables
#---------------------------------------
SettingsFile = os.path.join(os.path.dirname(__file__), "FSSettings.json")
ScriptSettings = None                                                                                                   #Settings to be used from chatbot interface
    
#timer related
tTickCD = None                                                                                                          #the cooldown for tick()
tLastTick = None   

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
    """
        Load in saved settings file if available else set default values.
    """
    def __init__(self, settingsfile=None):
        try:
            with codecs.open(SettingsFile, encoding="utf-8-sig", mode="r") as f:
                self.__dict__ = json.load(f, encoding="utf-8")
            self.initSuccess = True
        except:
            # load in variables from .json file if it fails to load
            self.initSuccess = False


    def reload(self, jsondata):
        """
            Reload settings from Chatbot user interface by given json data.
        """
        self.__dict__ = json.loads(jsondata, encoding="utf-8")
        return

    def save(self, settingsfile):
        """
            Save settings contained within to .json and .js settings files.
        """
        try:
            with codecs.open(SettingsFile, encoding="utf-8-sig", mode="w+") as f:
                json.dump(self.__dict__, f, encoding="utf-8")
            with codecs.open(SettingsFile.replace("json", "js"), encoding="utf-8-sig", mode="w+") as f:
                f.write("var settings = {0};".format(json.dumps(self.__dict__, encoding='utf-8')))
        except:
            Parent.Log(ScriptName, "Failed to save settings to file.")
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

    #   CODE
    if (data.IsChatMessage() and data.IsFromTwitch()):
        points4Messages(data.User, data.Message)
        fish(data)
        heist(data)
    return

def points4Messages(user, message):
    try:
        #   STEP 1: EGG
        if (message == "I am steak"):
            Parent.SendTwitchMessage("VoHiYo")

            if (user == "i_am_steak"):
                Parent.AddPoints(user, 500)

        #   STEP 2: POINTS PER CHAT MESSAGE
        if (message[0] != '!'):
            Parent.AddPoints(user, rand.randint(3, 10))

    except Exception as e:
        Parent.SendTwitchWhisper("i_am_steak", e.message)
        Parent.SendTwitchWhisper("i_am_not_steak", e.message)
    return
   
def fish(data):
    global activeFish
    global recFish1
    global recFish2

    #PART 1: FISH SWITCH
    if (((data.User == "tiltasaurus") or (data.User == "i_am_steak") or (data.User == "i_am_not_steak")) and (data.Message == '!fish')):             #check if !fish
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
                i = rand.randint(1, 100)                                                                            #get fish size
                sTmp = data.User + " found a rare Tilted PowerUpL SabaPing PowerUpR worth " + str(i) + " points!"
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

        if ((sTmp == "!heist") and (bHeistTmr1 == False)):
            sTmp = ""
            for i in range(7, len(data.Message)):
                sTmp = sTmp + data.Message[i]

            try:
                iTmp = int(sTmp)
                lTmp = long(sTmp)

                if ((len(lHeisters) == 0) and (iTmp > 0)):
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
        heistTick()

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
        bHeistTmr1 = False
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
        Parent.SendTwitchWhisper("i_am_not_steak", sOut)

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
