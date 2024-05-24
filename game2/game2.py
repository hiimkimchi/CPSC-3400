#Bryan Kim
#CPSC 3400
#game2.py

import random
import re
import sys

# 100MB of characters
NUM_BYTES = (1024 ** 2) * 100
HEIGHT = 8
WIDTH = 8
STRENGTH = 9
CELL_WIDTH = 11

ANSI_CYAN = "\033[96m"
ANSI_END = "\033[0m"
ANSI_GREEN = "\033[92m"
ANSI_RED = "\033[91m"

#few comments will be added to existing code for understanding
class Alien:
    def __init__(self, board, coords, strength, isBomb):
        self.board = board
        self.coords = coords
        self.strength = strength
        self.board.addAlien(self)
        self.x = coords[0]
        self.y = coords[1]
        #important value for garbage collection
        self.squished = False
        self.value = bytearray(NUM_BYTES)
        self.children = []
        #isBomb and countdown is specific to the new bomb aliens
        self.isBomb = isBomb
        self.countdown = 3 if self.isBomb else None

    #print the strength as red
    def __str__(self):
        if(self.isBomb):
            return ANSI_CYAN + str(self.strength) + ANSI_END
        return ANSI_RED + str(self.strength) + ANSI_END

    #once squished, mark it for sweep
    def doDeath(self):
        self.squished = True
        self.board.clearCell(self.coords)

    #alien is popped (killed) when strength is reduced to none
    def doPop(self, strength=1):
        self.strength -= strength
        if self.strength < 1:
            self.doDeath()

    def doGrow(self):
        chance = random.randint(0, 9)
        if self.strength < STRENGTH and chance > 7:
            self.strength += 1

    #takes a turn
    def doTimestep(self):
        self.doTravel()
        self.doSpawn()
        self.doGrow()

        if(self.isBomb):
            self.countdown -= 1
            if(self.countdown < 0):
                print("Bomb exploded! You lose.")
                exit(0)

    def doTravel(self):
        distx = random.randint(-1, 1)
        disty = random.randint(-1, 1)
        newx = self.x + distx
        newy = self.y + disty
        if self.inRange((newx, newy)):
            self.board.moveAlien(self.coords, (newx, newy))
            self.coords = (newx, newy)
    
    def doSpawn(self):
        emptySpace = self.findEmptySpace()
        neighbor = self.getNeighbor()
        chance = random.randint(0, 9)
        bombChance = random.randint(0, 9)
        if neighbor != None and emptySpace != None and chance > 6:
            child = Alien(self.board, emptySpace, max(1, self.strength - 1), False)
            self.children.append(child)
        
        #adds another conditional that may create a bomb alien instead of a regular one
        elif neighbor != None and emptySpace != None and bombChance > 6:
            child = Alien(self.board, emptySpace, max(1, self.strength - 1), True)
            self.children.append(child)

    def findEmptySpace(self):
        adjacent = [(self.x + 1, self.y + 1), (self.x + 1, self.y), (self.x + 1, self.y - 1),
                    (self.x, self.y + 1), (self.x, self.y - 1), (self.x - 1, self.y - 1),
                    (self.x - 1, self.y), (self.x - 1, self.y + 1)]
        random.shuffle(adjacent)
        for coords in adjacent:
            if self.inRange(coords) and self.board.isEmpty(coords):
               return coords
        return None

    def getNeighbor(self):
        adjacent = [(self.x + 1, self.y + 1), (self.x + 1, self.y), (self.x + 1, self.y - 1),
                    (self.x, self.y + 1), (self.x, self.y - 1), (self.x - 1, self.y - 1),
                    (self.x - 1, self.y), (self.x - 1, self.y + 1)]
        neighbors = []
        for coords in adjacent:
            if self.inRange(coords):
                neighbor = self.board.getAlien(coords)
                if neighbor != None:
                    neighbors.append(neighbor)
        if len(neighbors) == 0:
            return None
        neighbor = neighbors[random.randint(0, len(neighbors) - 1)]
        return neighbor

    def inRange(self, coords):
        if coords[0] > 0 and coords[0] < self.board.width and coords[1] > 0 and coords[1] < self.board.height:
            return True
        return False

class Board:
    def __init__(self, height, width):
        self.board = [[None for j in range(width)] for i in range(height)]
        self.height = height
        self.width = width

    def __str__(self):
        string = ""
        for i in range(self.width):
            cells1 = []
            cells2 = []
            for j in range(self.height):
                alien = self.getAlien((i, j))
                cell1 = "|    -     ".format(alien)
                if alien != None and alien.squished == False:
                    cell1 = "|    {0}     ".format(alien)
                cell2 = "| ({0:02d},{1:02d})  ".format(i, j)
                if j == (self.height - 1):
                    cell1 += '|'
                    cell2 += '|'
                cells1.append(cell1)
                cells2.append(cell2)
            string += '-' * ((len(cells1) * CELL_WIDTH) + 1)
            string += '\n'
            for cell in cells1:
                string += cell
            string += '\n'
            for cell in cells2:
                string += cell
            string += '\n'
            if i == (self.width - 1):
                string += '-' * ((len(cells1) * CELL_WIDTH) + 1)
                string += '\n'
        return string

    def addAlien(self, alien):
        coords = alien.coords
        self.board[coords[0]][coords[1]] = alien

    def clearCell(self, coords):
        self.board[coords[0]][coords[1]] = None

    def doTimestep(self):
        for i in range(self.width):
            for j in range(self.height):
                alien = self.getAlien((i, j))
                if alien != None and alien.squished == False:
                    alien.doTimestep()

    def getAlien(self, coords):
        return self.board[coords[0]][coords[1]]

    def isEmpty(self, coords=None):
        if coords == None:
            flag = 0
            for i in range(self.width):
                for j in range(self.height):
                    if self.getAlien((i, j)) != None:
                        flag = 1
                        return False
            return True
        if self.getAlien(coords) != None:
            return False
        return True

    def moveAlien(self, oldCoords, newCoords):
        if not self.isEmpty(oldCoords) and self.isEmpty(newCoords):
            alien = self.getAlien(oldCoords)
            self.clearCell(oldCoords)
            self.board[newCoords[0]][newCoords[1]] = alien

    #if coords are invalid, skip turn. else, pop the alien
    def squish(self, coords, player, strength=1):
        if coords[0] < 0 or coords[0] >= self.width:
            print("Invalid coordinates. Lose your turn.")
            return -1
        elif coords[1] < 0 or coords[1] >= self.height:
            print("Invalid coordinates. Lose your turn.")
            return -1
        #if cell is empty, lose a life
        elif self.isEmpty(coords):
            print("Cell is empty. Lose 1 life.")
            player.loseLife()
            return -1
        else:
            alien = self.getAlien(coords)
            if alien != None:
                score = strength if alien.strength > strength else alien.strength
                alien.doPop(strength)
                return score
        return -1

class Player:
    def __init__(self, board, troops, bombs):
        self.board = board
        self.score = 0
        self.lives = 3
        self.strength = 1
        self.turn = 0

    def __str__(self):
        width = self.board.width
        size = (width * CELL_WIDTH) + 1
        string = "LIVES: {0}\tTURN: {1}\tSTRENGTH: {2}\tSCORE: ".format(self.lives, self.turn, self.strength)
        if self.score > 0:
            string += ANSI_GREEN + str(self.score) + ANSI_END
        elif self.score == 0:
            string += str(self.score)
        else:
            string += ANSI_RED + str(self.score) + ANSI_END
        return "{0:^{1}}".format(string, size)
    
    def loseLife(self):
        self.lives -= 1

    def doTimestep(self):
        self.turn += 1

#prints tree as strength(depth):strength(depth):etc
def printTree(alien, depth=0):
    tree = "{0}({1}):".format(str(alien), depth)
    if len(alien.children) == 0:
        return tree
    else:
        for child in alien.children:
            tree += printTree(child, depth + 1)
    return tree

#prints each tree 
def printTrees(aliens):
    for alien in aliens:
        tree = printTree(alien)
        print(tree)

#desc: finds killed aliens and removes them. makes sure to link orphaned children to grandparents when a nonleaf node is swept.
#      this is done to save memory, as the Aliens are very large.
#pre : -alien is passed in as an Alien object
#post: -all aliens that are marked as squished are deleted from memory
def sweep(alien):
    #simply deletes child alien if it is a leaf
    if len(alien.children) == 0:
        if (alien.squished):
            alien = None
        return
    #link ALIVE children that would be lost when dead alien is removed
    #requires access to three depths in the tree
    elif len(alien.children) > 1:
        for child in alien.children:
            for grandchild in child.children:
                if(child.squished):
                    alien.children.append(grandchild)
            if(child.squished):
                child = None
    #iterate through the alien's childrens
    else:
        for child in alien.children:
            sweep(child)
    return

#desc: uses the sweep function provided above to delete all dead aliens in one timestep
#pre : -a list of aliens is passed in
#post: -all dead aliens are removed from memory
def sweepAliens(aliens):
    for alien in aliens:
        sweep(alien)

#NEW ADDITIONS
#-added a lose condition by keeping track of lives
#-added a bomb alien
#   -after 3 iterations with no death, bomb alien will explode and end the game
#   -bomb aliens are noted with cyan font color
if __name__ == "__main__":
    #if arg is provided when executed in command line, use it as the seed
    seed = 0
    if len(sys.argv) > 1:
        seed = sum([ord(c) for c in sys.argv[1]])
    random.seed(seed)
    aliens = []
    board = Board(HEIGHT, WIDTH)

    #decided not to implement troops or bombs
    player = Player(board, 3, 3)
    userin = ""
    #welcome message
    print("Welcome to the game. Your objective is to kill aliens.\nYou have 3 lives.\nRed aliens are regular, and blue aliens are bomb aliens that will explode after 3 turns.")
    while(userin.upper() != "QUIT" and userin.upper() != "EXIT"):
        x = random.randint(0, WIDTH - 1)
        y = random.randint(0, HEIGHT - 1)
        s = random.randint(1, STRENGTH)
        if player.turn == 0:
            s = 5
        if board.isEmpty((x, y)):
            #game will always start with a non bomb alien
            alien = Alien(board, (x, y), s, False)
            aliens.append(alien)
        print(board)
        print(player)
        userin = input("Choose a coordinate to attack (x,y): ")
        search = re.search(r"\(?(-?\d+)[, ]+(-?\d+)\)?", userin)
        (userx, usery) = search.groups() if search != None else (None, None)
        if userx == None or usery == None:
            if userin.upper() == "QUIT" or userin.upper() == "EXIT":
                continue
            elif userin.upper() == "TREES":
                printTrees(aliens)
                continue
            print("Invalid coordinates. Lose your turn.")
        else:
            userx = int(userx)
            usery = int(usery)
            score = board.squish((userx, usery), player, player.strength)
            if score > 0:
                player.strength += 1 if player.strength < STRENGTH else 0
            elif score <= 0:
                player.strength -= 1 if player.strength > 1 else 0
            player.score += score
        
        #after each timestep, do sweeping
        sweepAliens(aliens)

        board.doTimestep()
        player.doTimestep()
        if board.isEmpty():
            print("All aliens destroyed. You win!")
            exit(0)

        #if the lives are 0 or less, lose.
        if (player.lives <= 0):
            print("All lives lost. You lose.")
            exit(0)
        
        #if there are over 25 aliens, lose.
        if(len(aliens) > 25):
            print("Over 25 aliens swarmed you! You lose.")
            exit(0)