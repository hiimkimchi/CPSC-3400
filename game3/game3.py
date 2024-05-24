#Bryan Kim
#CPSC 3400
#game3.py

import json
import re
import sys
import time

#JSON requirements:
# - every room must have at least one way to leave and it must link with the overall scope of the board.
# - every room may have 0-10 objects.
#   - every object will only have one interactionID if USE is in their interaction list
#   - every healing object will be true for isMed
#   - every weapon object will be true for isWeapon
# - every room may have 0-10 enemies.
# - the first room must be "entrance" and the last room must be "exit"
#syntax requirements have been ommitted, just look at the sample json for that.

class Player:
    def __init__ (self):
        self.health = 100
        self.objects = []
        self.isAlive = True
    
    def __str__(self):
        if self.health <= 0:
            self.health = 0
        return "Health: " + str(self.health) + "\n"
    
    def getHit(self, power):
        self.health -= power
        if self.health <= 0:
            self.doDeath()

    def doDeath(self):
        self.isAlive = False

    def showInventory(self):
        if len(self.objects) == 0:
            print("Your pockets are empty...")
        else:
            print("INVENTORY:")
            for obj in self.objects:
                print(obj)
    
    def heal(self, amount):
        #if health is less than 100, heal by amount
        if self.health < 100:
            self.health += amount
        
        #if item overheals, set to 100
        if self.health > 100:
            self.health = 100
        print("Gained " + str(amount) + " Health!")
        print(self)


    def getStatus(self):
        return self.isAlive
        
    def hit(self, enemy, power, currentRoom):
        enemy.getHit(power)
        print("Hit " + enemy.enemyID + " for " + str(power) + " HP!")
        if not enemy.isAlive:
            enemy.deathMessage()
            currentRoom.enemies.remove(enemy)

class Room:
    def __init__ (self, roomID, north, south, east, west, objects, enemies, desc, isLocked):
        self.roomID = roomID
        self.desc = desc
        self.north = north
        self.south = south
        self.east = east
        self.west = west
        self.objects = objects
        self.enemies = enemies
        self.isLocked = isLocked
    
    def __str__(self):
        string = self.desc + "\nITEMS AVAILABLE FOR INTERACTION:\n"
        for item in self.objects:
            string += str(item)
        return string

    def unlock(self):
        if self.isLocked == True:
            self.isLocked = not self.isLocked

class Object:
    def __init__ (self, objID, desc, interactions, interactionID, power, isWeapon, isMed):
        self.objID = objID
        self.desc = desc
        self.interactions = interactions
        self.interactionID = interactionID
        self.power = power
        self.isWeapon = isWeapon
        self.isMed = isMed
    
    def __str__(self):
        string = ""
        #weapon will have a "power" line
        if self.isWeapon:
            string += "\nObject: {0}\nPower: {1}".format(self.objID, self.power)
            string += "\nInteractions: "
            for i in self.interactions:
                string += i
                string += " "
            string += "\n"
            return string
        #meds will have a "hp gain" line
        elif self.isMed:
            string += "\nObject: {0}\nHP Gain: {1}".format(self.objID, self.power)
            string += "\nInteractions: "
            for i in self.interactions:
                string += i
                string += " "
            string += "\n"
            return string
        else:
            string += "\nObject: " + self.objID
            string += "\nInteractions: "
            for i in self.interactions:
                string += i
                string += " "
            string += "\n"
            return string
    
    def getID(self):
        return self.objID
    
    def strengthen(self):
        self.power *= 2

class Enemy:
    def __init__ (self, enemyID, desc, health, power):
        self.enemyID = enemyID
        self.desc = desc
        self.health = health
        self.power = power
        self.isAlive = True
    
    def __str__(self):
        return "\nIt's " + self.enemyID + "!\n" + "Health: " + str(self.health) + "\n" + "Attack Power: " + str(self.power) + "\n"
    
    def getHit(self, power):
        self.health -= power
        if self.health <= 0:
            self.doDeath()

    def getStatus(self):
        if self.isAlive:
            return self.isAlive
        else:
            return not self.isAlive
    
    def doDeath(self):
        self.isAlive = False
    
    def hit(self, player):
        player.getHit(self.power)
        print(self.enemyID + " hit you for " + str(self.power) + " HP!")
        print(player)
        if player.health <= 0:
            player.doDeath()
    
    def deathMessage(self):
        print(self.desc)




def printMenu():
    print("This text adventure game will use key inputs (PLEASE SEPERATE WORDS WITH A SINGLE SPACE):\n"
        "\n- GO <direction>: you will travel in the direction you choose if there is a room available."
        "\n- TAKE <object>: you will take an object in the room if it is available."
        "\n- OPEN <object>: you will open a door if you hold the correct key"
        "\n- USE <object> (<object>): you will use an object in the room to do some action. if there are two objects you can use together,\nthe first will be used on the second."
        "\n- LOOK <direction> | <object> | <nothing>: if you specify a direction, the description of the room in the direction will print."
        " same with an object. \nif no arguments are added, description of the room will print."
        "\n- THROW <object>: throw an object. will do double damage to enemies if it is a weapon. if thrown, you will never see it again!"
        "\n- ATTACK <enemy> WITH <object>: will attack enemy with object."
        "\n- INVENTORY: will list the items you have."
        "\n- HELP: will print these instructions again."
        "\n\nYour goal is to survive and find the exit."
        "\nIf a room has an enemy, they will attack you every turn until you defeat it.\n")

#desc: will handle all userinput for the game
#pre : -userinput and the current Room object will be passed in
#post: -if the user does not go to a new room, return current room.
#      -if the user goes to a new room, return respective room.
def handleInput(inString, currentRoom, rooms, player):
    inventoryPattern = re.compile(r"^INVENTORY$")
    helpPattern = re.compile(r"^HELP$")
    goPattern = re.compile(r"^GO$")
    takePattern = re.compile(r"^TAKE$")
    openPattern = re.compile(r"^OPEN$")
    usePattern = re.compile(r"^USE$")
    lookPattern = re.compile(r"^LOOK$")
    throwPattern = re.compile(r"^THROW$")
    attackPattern = re.compile(r"^ATTACK$")
    direction = re.compile(r"^(NORTH|SOUTH|EAST|WEST)$")
    inputArr = parseInput(inString)
    print(inputArr)
    #if the userinput matches INVENTORY option, print player inventory
    if re.search(inventoryPattern, inputArr[0]) != None:
        player.showInventory()
        return currentRoom
    
    #if the userinput matches HELP option, print menu
    elif re.search(helpPattern, inputArr[0]) != None:
        printMenu()
        print("Scroll up to view.")
        return currentRoom

    #if the userinput matches GO option, handle accordingly
    elif re.search(goPattern, inputArr[0]) != None:
        if len(inputArr) != 2:
            print("Where are you trying to go?")
            return currentRoom
        else:
            if re.search(direction, inputArr[1]) != None:
                #retrieve new room
                roomName = chooseDir(inputArr[1], currentRoom)
                newRoom = None

                #if the direction is not valid ("NO"), then put error message
                if roomName == "NO":
                    print("Looks like you can't go there. Watch yo step.")

                #if the direction is valid
                else:
                    # Find the corresponding room object in the rooms list
                    for room in rooms:
                        if room.roomID == roomName:
                            newRoom = room
                            break

                    #print locked message
                    if newRoom.isLocked:
                        print("This room is locked! Looks like you'll have to find a way to open it...")
                    #move and put confirmation message
                    else:
                        print("Moving rooms")
                        return newRoom
            else:
                print("Not a valid direction! (north, south, east, west)")
        return currentRoom

    #if the userinput matches TAKE option, handle accordingly
    elif re.search(takePattern, inputArr[0]) != None:
        if len(inputArr) != 2:
            print("What are you trying to take?")
            return currentRoom
        index, found = checkValidity(currentRoom, takePattern, inputArr[1])

        #if valid object is found
        if found:
            #put object in inventory and remove from room
            keyObject = currentRoom.objects.pop(index)
            keyObject.interactions.remove("TAKE")
            player.objects.append(keyObject)
            print("Got " + keyObject.getID() + "!")
        else:
            print("Takeable object not selected in the room.")
        return currentRoom

    #if the userinput matches OPEN option, handle accordingly
    elif re.search(openPattern, inputArr[0]) != None:
        if len(inputArr) != 2:
            print("What are you trying to open?")
        else:
            keyHeld = False
            index, found = checkValidity(currentRoom, openPattern, inputArr[1])

            #if valid object is found
            if found:
                for item in player.objects:
                    #if in your inventory, there is a key that unlocks the object you specify, keyHeld = true.
                    if len(item.interactionID) > 0:
                        if "unlocks" in item.interactionID[0] and item.interactionID[0].get("unlocks").upper() == inputArr[1]:
                            keyHeld = True

                #if key is held, open the corresponding room
                if keyHeld:
                    roomName = currentRoom.objects[index].interactionID[0].get("DOORLINK")
                    linkedRoom =  None
                    for room in rooms:
                        if roomName == room.roomID:
                            linkedRoom = room
                            break
                    currentRoom.objects.remove(currentRoom.objects[index])
                    linkedRoom.isLocked = False
                    print(inputArr[1] + " opened!")
                #else, notify player that you need a key
                else:
                    print("Looks like you need to be holding a specific key...")
            else:
                print("Openable object not selected in the room!")
        return currentRoom

    #if the userinput matches USE option, handle accordingly
    elif re.search(usePattern, inputArr[0]) != None:
        if len(inputArr) < 2:
            print("You need to specify which object to use!")
        else:
            indexRoom, foundRoom = checkValidity(currentRoom, usePattern, inputArr[1])
            indexPlayer, foundPlayer = checkValidity(player, usePattern, inputArr[1])

            #if valid object is found from the room
            if foundRoom:
                #if it is a medical item, use and discard.
                if currentRoom.objects[indexRoom].isMed:
                    player.heal(currentRoom.objects[indexRoom].power)
                    currentRoom.objects.remove(currentRoom.objects[indexRoom])
                #if the object's use case is strengthening
                elif "strengthens" in currentRoom.objects[indexRoom].interactionID[0]:
                    #print error message because you need a tool and strengthener
                    if len(inputArr) != 3:
                        print("You need to specify which item you strengthen!")
                    #strengthen 
                    else:
                        strengtheneeName = currentRoom.objects[indexRoom].interactionID[0].get("strengthens")
                        for item in player.objects:
                            if item.objID == strengtheneeName and strengtheneeName == inputArr[2]:
                                item.strengthen()
                                print("Your " + item.objID + " has been strengthened. It has double the power now!")
                                return currentRoom
                        print("Compatible item not found!")
                else:
                    print("No usage specified for this object. This is a bug.")

            elif foundPlayer:
                #if it is a medical item, use and discard.
                if player.objects[indexPlayer].isMed:
                    player.heal(player.objects[indexPlayer].power)
                    player.objects.remove(player.objects[indexPlayer])
                #if it is one of three items needed to go to the exit door, countdown until 0.
                elif "countdown" in player.objects[indexPlayer].interactionID[0]:
                    for item in currentRoom.objects:
                        if item.objID == "TripleLockedDoor":
                            item.power -= 1
                            if item.power == 0:
                                roomName = item.interactionID[0].get("DOORLINK")
                                linkedRoom =  None
                                for room in rooms:
                                    if roomName == room.roomID:
                                        linkedRoom = room
                                        break
                                currentRoom.objects.remove(currentRoom.objects[index])
                                linkedRoom.isLocked = False
                                print(linkedRoom.roomID + " opened!")
                            else:
                                print(str(item.power) + " items left to open the door.")
                        else:
                            print("I don't think it's the right place to use this...")
                else:
                    print("No usage specified for this object. This is a bug.")
            else:
                print("Usable object not selected in the room!")
        return currentRoom
        
    #if the userinput matches LOOK option, handle accordingly
    elif re.search(lookPattern, inputArr[0]) != None:
        #if there are a correct number of arguments
        if len(inputArr) == 2:
            #search for the room desc of a direction. if the direction = "NO", then no desc.
            if re.search(direction, inputArr[1]) != None:
                roomName = chooseDir(inputArr[1], currentRoom)
                newRoom = None
                if roomName != "NO":
                    for room in rooms:
                        if room.roomID == roomName:
                            newRoom = room
                            break
                    print(newRoom.desc)
                else:
                    print("Nothing is in this direction.")

            #else, check objects
            #no need to check for validity, all objects should allow look
            else:
                #search through inventory and room to see if they are the object in question. if neither, say not found.
                for item in currentRoom.objects:
                    if item.objID.upper() == inputArr[1]:
                        print(item.desc)
                        return currentRoom
                for item in player.objects:
                    if item.objID.upper() == inputArr[1]:
                        print(item.desc)
                        return currentRoom
                print("Object not found.")
        #if there is only one argument, print description of the room (which is in every turn, so just return)
        else:
            print("Printing current room info...")
        return currentRoom

    #if the userinput matches THROW option, handle accordingly
    elif re.search(throwPattern, inputArr[0]) != None:
        indexRoom, foundRoom = checkValidity(currentRoom, throwPattern, inputArr[1])
        indexPlayer, foundPlayer = checkValidity(player, throwPattern, inputArr[1])

        #if the object is found in the room
        if foundRoom:
            if currentRoom.objects[indexRoom].isWeapon:
                if len(currentRoom.enemies) > 0:
                    for enemy in currentRoom.enemies:
                        player.hit(enemy, currentRoom.objects[indexRoom].power, currentRoom)
                    print("Dealt " + str(currentRoom.objects[indexRoom].power) + " damage to all enemies.")
                    if len(currentRoom.objects[indexRoom].interactionID) > 0:
                        print(currentRoom.objects[indexRoom].interactionID[0].get("ONTHROW"))
                else:
                    print("But no damage was done to anything.")
            #throw the item by removing it from the list. if it has a special throw message, print it.
            else:
                print("Threw " + currentRoom.objects[indexRoom].objID + ".")
                if len(currentRoom.objects[indexRoom].interactionID) > 0:
                    print(currentRoom.objects[indexRoom].interactionID[0].get("ONTHROW"))
            currentRoom.objects.remove(currentRoom.objects[indexRoom])

        #if the object is found in the inventory
        elif foundPlayer:
            #throw the item by removing it from the list. if it is a weapon, deal double weapon's damage. if not, print throw message if exists.
            print("Threw " + player.objects[indexPlayer].objID + ".")
            if player.objects[indexPlayer].isWeapon:
                if len(currentRoom.enemies) > 0:
                    print("Dealt " + str(player.objects[indexPlayer].power * 2) + " damage to all enemies.")
                    for enemy in currentRoom.enemies:
                        player.hit(enemy, player.objects[indexPlayer].power * 2, currentRoom)
                else:
                    print("But no damage was done to anything.")
            else:
                if len(player.objects[indexPlayer].interactionID) > 0:
                    print(player.objects[indexPlayer].interactionID[0].get("ONTHROW"))
            player.objects.remove(player.objects[indexPlayer])
        else:
            print("Throwable object not selected in the room.")
        return currentRoom


    #if the userinput matches ATTACK option, handle accordingly
    elif re.search(attackPattern, inputArr[0]) != None:
        if len(inputArr) != 4:
            print("Attack ___ with ___?")
        else:
            currentEnemy = None
            currentWeapon = None
            for enemy in currentRoom.enemies:
                if inputArr[1] == enemy.enemyID:
                    currentEnemy = enemy
            
            for weapon in player.objects:
                if inputArr[3] == weapon.objID:
                    if weapon.isWeapon:
                        currentWeapon = weapon
                    else:
                        print("This isn't a weapon! Dealt 0 damage.")
            
            if currentEnemy == None:
                print("This enemy doesn't exist.")
            elif currentWeapon == None:
                print("This weapon doesn't exist.")
            else:
                player.hit(currentEnemy, currentWeapon.power, currentRoom)
        return currentRoom

    #else, say the input was invalid
    else:
        print("Invalid input, try again.")
        return currentRoom


#desc: splits input by spaces
#pre : -input string is passed in
#post: -array of strings is returned
def parseInput(inString):
    return inString.split()

#desc: checks the validity of an object in an inventory
#pre : -currentInventory, pattern, and input is passed in
#post: -will return int, bool tuples
def checkValidity(currentRoom, pattern, inString):
    index = 0
    found = False
    for item in currentRoom.objects:
        if inString == item.objID.upper():
            for j in item.interactions:
                if re.search(pattern, j) != None:
                    found = True
                    break
        if found:
            break
        index += 1
    return index, found

#desc: chooses a direction name
#pre : -input string and currentRoom is passed in
#post: -returns a string representing room's name in direction
def chooseDir(inString, currentRoom):
    roomName = None
    if inString == "NORTH":
        roomName = currentRoom.north
    elif inString == "SOUTH":
        roomName = currentRoom.south
    elif inString == "EAST":
        roomName = currentRoom.east
    elif inString == "WEST":
        roomName = currentRoom.west
    return roomName

#desc: pauses for 5 seconds
#pre : none
#post: none
def pause():
    for i in range(5):
        time.sleep(0.3)
        print(".")
        

if __name__ == "__main__":
    isWon = False
    rooms = []
    player = Player()
    with open("bkim7.json") as file:
        data = json.load(file)
    
    #add every room in rooms list
    for key, roomData in data.items():
        currentItems = []
        currentEnemies = []

        #specifically search for objects and add them as Object objects
        if "objects" in roomData:
            for objData in roomData["objects"]:
                interactionPair = []
                if "interactionID" in objData:
                    interactionPair = objData.get("interactionID")
                currentItems.append(Object (objData["objID"], objData["description"], objData["interactions"], interactionPair, objData["power"], objData["isWeapon"], objData["isMed"]))

        #search for enemies and add them as Enemy objects
        if "enemies" in roomData:
            for enemyData in roomData["enemies"]:
                currentEnemies.append(Enemy (enemyData["enemyID"], enemyData["description"], enemyData["health"], enemyData["power"]))

        currentRoom = Room(key, roomData.get("north"), roomData.get("south"), roomData.get("east"), roomData.get("west"), currentItems, currentEnemies, roomData.get("description"), roomData.get("isLocked"))
        rooms.append(currentRoom)
    
    #set the current room = the entrance. previous room will ensure that the player doesn't get attacked on the first step they enter a room.
    currentRoom = rooms[0]
    previousRoom = currentRoom

    #prints welcome message and instructions. Watiting is for style.
    print("Welcome to Office Apocalypse!\nYou work at a boring 9-5 at a big finance firm, but all of a sudden, the Z virus breaks out!"
          "\nAll of your coworkers are zombies now, what will you do???")
    
    pause()

    printMenu()
    print("\n\nGame will start in 5 seconds!")
    time.sleep(5)
    for i in range(30):
        print()
    
    while not isWon and player.health > 0:
        print(currentRoom)
        print(player)
        #if there is an enemy, begin combat.
        if len(currentRoom.enemies) > 0:
            for enemy in currentRoom.enemies:
                print(enemy)
            
        userin = input("What to do? (\"HELP\" will print the instructions again.): ").upper()
        currentRoom = handleInput(userin, currentRoom, rooms, player)
        pause()

        #set the currentRoom = previous room. gives buffer to allow player to not immediately get hit as they enter the room.
        if previousRoom != currentRoom:
            previousRoom = currentRoom
        else:
        #enemies will damage player after every turn
            if len(currentRoom.enemies) > 0:
                for enemy in currentRoom.enemies:
                    enemy.hit(player)
                pause()

        #if the current room is the exit, you won
        if currentRoom.roomID == "exit":
            isWon = True

        #if you died, you lose.
        if not player.getStatus():
            print("You died! Thanks for playing Office Apocalypse.")
            sys.exit(0)
    print("You escaped! Thanks for playing Office Apocalypse.")