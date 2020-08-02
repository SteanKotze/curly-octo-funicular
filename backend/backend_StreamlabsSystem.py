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
Version = "0.2"
Description = "This script are do many heist (/O.O)/"

#---------------------------------------
#   Set Variables
#---------------------------------------
settings_path = "Services\\Scripts\\backend\\backend_settings.json"
settings = None
    
#timer related
tick_refresh_rate = None                                                                                                          #the cooldown for tick()
last_tick = None   

#fish related
fish_minimum_payout = None
fish_maximum_payout = None
fish_catch_chance = None
fish_event_start_permission = None
fish_event_active = None
fish_size_record = None
fish_user_record = None 

#heist related
heist_user_limit = None
heist_cooldown = None                                                                                                       #time between heists
next_heist_start_time = None                                                                                                       #timer till next heist
heist_active = None
heist_join_time = None                                                                                                       #time to enter heist
heist_start_time = None                                                                                                       #timer till heist starts
heist_start_time_active = None

heisters = None                                                                                                        #list of heisters participating in current heist
heisters_inputs = None                                                                                                          #list of money each heister as input into the pool
previous_heisters = None                                                                                                         #list of names that have modified win chances
previous_heisters_chance = None                                                                                                        #list of chances to win for each modified name

# Points Per Message Variables
points_per_message = None

#---------------------------------------
#   [Required] Intialize Data 
#---------------------------------------
def Init():
    #   GLOBALS
    global settings_path
    global settings
    
    global tick_refresh_rate

    global heist_user_limit
    global heist_cooldown
    global heist_join_time
    
    global last_tick

    global fish_minimum_payout
    global fish_maximum_payout
    global fish_catch_chance
    global fish_event_start_permission
    global fish_event_active
    global fish_size_record
    global fish_user_record

    global next_heist_start_time
    global heist_active
    global heist_start_time
    global heist_start_time_active

    global heisters
    global heisters_inputs
    global previous_heisters
    global previous_heisters_chance

    global heist_payout
    global heist_user_limit

    global points_per_message

    #   CODE
    with codecs.open(settings_path, encoding="utf-8-sig", mode="r") as settings_file:
        settings = json.load(settings_file, encoding="utf-8")
        
    if (settings != None):
        tick_refresh_rate = int(settings['tick_refresh_rate'])

        fish_minimum_payout = int(settings['fish_minimum_value'])
        fish_maximum_payout = int(settings['fish_maximum_value'])
        fish_catch_chance = float(settings['fish_catch_chance'])
        fish_event_start_permission = settings['fish_permission'].split(',')
        
        heist_user_limit = int(settings['heist_user_limit'])
        heist_join_time = int(settings['heist_join_time'])
        heist_cooldown = int(settings['heist_cooldown'])

        heist_payout = float(settings['heist_payout'])
        heist_user_limit = int(settings['heist_user_limit'])

        points_per_message = int(settings['points_per_message'])

    else:
        tick_refresh_rate = 5

        fish_minimum_payout = 10
        fish_maximum_payout = 40
        fish_catch_chance = 0.25
        fish_event_start_permission = ['Tiltasaurus','I_am_steak']

        heist_user_limit = 15
        heist_join_time = 60
        heist_cooldown = 600

        heist_payout = 1.25
        heist_user_limit = 15

        points_per_message = 5

    last_tick = t.time() - tick_refresh_rate

    fish_event_active = False
    fish_size_record = 0
    fish_user_record = ""

    next_heist_start_time = t.time()
    heist_active = False
    heist_start_time = t.time()
    heist_start_time_active = False

    heisters = []
    heisters_inputs = []
    previous_heisters = []
    previous_heisters_chance = []

    return

#---------------------------------------
#   [Required] Execute Data / Process Messages
#---------------------------------------
def Execute(data):
    if (data.IsChatMessage() and data.IsFromTwitch()):
        points_per_chat_message(data.User, data.Message)
        fish(data)
        heist(data)

    return

def points_per_chat_message(user, message):
    global points_per_message

    try:
        if (message == "I am steak"):
            Parent.SendTwitchMessage("VoHiYo")

            if (user == "i_am_steak"):
                Parent.AddPoints(user, 500)

        if (message[0] != '!'):
            Parent.AddPoints(user, points_per_message)

    except Exception as e:
        Parent.SendTwitchWhisper("i_am_steak", e.message)
        Parent.SendTwitchWhisper("i_am_not_steak", e.message)

    return
   
def fish(data):
    global fish_minimum_payout
    global fish_maximum_payout
    global fish_catch_chance
    global fish_event_start_permission
    global fish_event_active
    global fish_size_record
    global fish_user_record

    if (((data.User == "tiltasaurus") or (data.User == "i_am_steak") or (data.User == "i_am_not_steak")) and (data.Message == '!fish')):
        if (fish_event_active == False):
            fish_event_active = True
            response_string = "A school of fish is passing through a lake nearby! Type any message with 'fish' in it to see if you can catch one."
            Parent.SendTwitchMessage(response_string)
            Parent.SendDiscordMessage(response_string)
        else:
            response_string = "The school of fish has passed! The largest fish caught was worth " + str(fish_size_record) + " and was caught by " + fish_user_record + "."
            Parent.SendTwitchMessage(response_string)
            Parent.SendDiscordMessage(response_string)
            fish_event_active = False
            fish_size_record = 0
            fish_user_record = ""

    if (fish_event_active == True):
        if ((("SabaPing" in data.Message) or ("fish" in data.Message)) and (data.Message != "fish")):
            rand.seed(t.time() + fish_size_record + rand.randint(1, 200))
            if (rand.randint(1, 100) < int(fish_catch_chance * 100)):
                fish_size = rand.randint(fish_minimum_payout, fish_maximum_payout)
                response_string = data.User + " caught a rare Tilted PowerUpL SabaPing PowerUpR worth " + str(fish_size) + " points!"
                Parent.SendTwitchMessage(response_string)

                Parent.AddPoints(data.User, fish_size)

                if (fish_size > fish_size_record):
                    fish_size_record = fish_size
                    fish_user_record = data.User

    return

def heist(data):
    global heist_user_limit
    global heist_cooldown
    global next_heist_start_time
    global heist_join_time
    global heist_start_time
    global heist_start_time_active

    global heisters
    global heisters_inputs
    global previous_heisters
    global previous_heisters_chance

    ### CODE
    if (data.Message.find('!heist') == 0):
        message = data.Message.split(' ')
        if (message[0] == "!heist"):
            if (next_heist_start_time > t.time()):
                minutes_to_next_heist = int(next_heist_start_time - t.time())/60
                response_string = data.User + " you will be able to heist again in " + str(minutes_to_next_heist) + " minutes"
                Parent.SendTwitchMessage(response_string)
                Parent.SendDiscordMessage(response_string)

            else:
                try:
                    heist_amount = int(message[1])

                    if ((len(heisters) == 0) and (heist_amount > 0)):
                        response_string = data.User + " is trying to get a team together in order to hit the nearest bank. In order to join type !heist (amount)"
                        Parent.SendTwitchMessage(response_string)
                        Parent.SendDiscordMessage(response_string)

                        heist_start_time = t.time() + heist_join_time
                        heist_start_time_active = True

                    if ((len(heisters) < heist_user_limit) and (data.User not in heisters) and (heist_amount > 0)):
                        if (Parent.GetPoints(data.User) >= long(heist_amount)):
                            Parent.RemovePoints(data.User, long(heist_amount))

                            heisters_inputs.append(heist_amount)
                            heisters.append(data.User)

                            if (len(heisters) > 1):
                                response_string = data.User + " joined the heist!"
                                Parent.SendTwitchMessage(response_string)
                                Parent.SendDiscordMessage(response_string)

                except:
                    Parent.SendTwitchMessage(data.User + ' the value you entered is not valid')
                    Parent.SendDiscordMessage(data.User + ' the value you entered is not valid')
    return

#---------------------------------------
#   [Required] Tick Function
#---------------------------------------
def Tick(): #DONE
    #   GLOBALS
    global tick_refresh_rate
    global last_tick

    #   CODE
    tTime = t.time()
    if (last_tick + tick_refresh_rate <= tTime):
        last_tick = tTime
        heistTick()

    return

def heistTick():
    #   GLOBALS
    global heist_user_limit
    global heist_cooldown
    global next_heist_start_time
    global heist_active
    global heist_join_time
    global heist_start_time
    global heist_start_time_active

    global heisters
    global heisters_inputs
    global previous_heisters
    global previous_heisters_chance

    ### CODE
    if ((heist_active == True) and (t.time() > next_heist_start_time)):
        heist_active = False
        response_string = "It looks like the cops have given up searching for the perpetrators. You can now heist again using !heist (amount)."
        Parent.SendTwitchMessage(response_string)
        Parent.SendDiscordMessage(response_string)

    elif ((heist_start_time_active == True) and (t.time() > heist_start_time)):
        heist_start_time_active = False
        next_heist_start_time = t.time() + heist_cooldown
        heist_active = True

        sList = []
        dList = []

        rand.seed(t.time() + len(heisters))
        iTmp = 0

        sOut = "Heist stats: "
        for i in range(0, len(heisters)):
            iTmp = rand.randint(0, 200)
            sOut = sOut + " #" + heisters[i] + " - " + str(iTmp)
            rand.seed(iTmp + t.time())

            if (heisters[i] in previous_heisters):                                                                              #check if modified win chance
                j = 0
                for j in range(0, len(previous_heisters)):
                    if (previous_heisters[j] == heisters[i]):
                        break

                iTmp2 = previous_heisters_chance[j]
                sOut = sOut + "," + str(iTmp2) 

                if (iTmp > iTmp2):
                    sList.append(heisters[i])                                                                          #success achieved

                    if ((iTmp2 > 50) and (iTmp2 < 70)):                                                                 #reduce percent to win by 5%
                        iTmp2 = iTmp2 + 5
                        previous_heisters_chance[j] = iTmp2
                        sOut = sOut + ",1"

                    elif (iTmp2 < 50):                                                                                  #reset win chances
                        if (len(previous_heisters) > 1):
                            previous_heisters = previous_heisters[0:j] + previous_heisters[j+1:] 
                            previous_heisters_chance = previous_heisters_chance[0:j] + previous_heisters_chance[j+1:]
                            sOut = sOut + ",2"

                        else:
                            previous_heisters = []
                            previous_heisters_chance = []
                            sOut = sOut + ",3"

                else:
                    dList.append(heisters[i])

                    if ((iTmp2 < 50) and (iTmp2 > 20)):                                                                 #reduce chance to lose by 10%
                        iTmp2 = iTmp2 - 10
                        previous_heisters_chance[j] = iTmp2
                        sOut = sOut + ",4"

                    elif (iTmp2 > 50):                                                                                  #reset win chances
                        if (len(previous_heisters) > 1):
                            previous_heisters = previous_heisters[0:j] + previous_heisters[j+1:] 
                            previous_heisters_chance = previous_heisters_chance[0:j] + previous_heisters_chance[j+1:]
                            sOut = sOut + ",5"

                        else:
                            previous_heisters = []
                            previous_heisters_chance = []
                            sOut = sOut + ",6"

            else: 
                previous_heisters.append(heisters[i])

                if (iTmp > 50):
                    sList.append(heisters[i])
                    previous_heisters_chance.append(55)

                else:
                    dList.append(heisters[i])
                    previous_heisters_chance.append(40)

        Parent.SendTwitchWhisper("i_am_steak", sOut)
        Parent.SendTwitchWhisper("i_am_not_steak", sOut)

        if (len(sList) > 0):
            iTot = 0                                                                                #get total input currency
            for i in range(0, len(heisters_inputs)):
                iTot = iTot + heisters_inputs[i]

            iTot = int(iTot * 1.25)

            iSus = 0                                                                                #get total input currency of succesful
            for i in range(0, len(heisters)):
                if (heisters[i] in sList):
                    iSus = iSus + heisters_inputs[i]

            sTmp = "Some of the crew got out of the bank with the loot! The results are: "
            j = 0
            for i in range(0, len(heisters)):

                if (heisters[i] in sList):
                    iTmp = int((float(heisters_inputs[i])/iSus)*iTot)
                    Parent.AddPoints(heisters[i], iTmp)
                    sTmp = sTmp + heisters[i] + " (" + str(iTmp) + ")"
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
                iTmp = rand.randint(0, 2*len(heisters))
                sTmp = heisters[i] + sTmp

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
                
        heisters = []
        heisters_inputs = []

    return