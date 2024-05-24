# Bryan Kim
# CPSC 3400
# game1.py
# This program runs a game that guesses an object based off a series of questions. It can be run with or without
# a provided database.

#in order to see the arguments made in terminal
import sys

#created a Node object based on specifications
class Node:
    def __init__(self, id, type, value, parent, left, right):
        self.id = id
        self.type = type
        self.parent = parent
        self.value = value
        self.left = left
        self.right = right

#desc: reads in a database file and creates a sorted list of all the questions and answers.
#      it also links children and parents together.
#pre : -program must only run with 2 arguments
#post: -returns a sorted list
def fileRead():
    try:
        #open file only if one argument is given (handled in main)
        file = open(sys.argv[1])
        paths = file.readlines()
        numOfNodes = len(paths)
        pathList = []

        #assume the input file is formated correctly
        for i in range(numOfNodes):
            branch = paths[i].split(':')
            id = int(branch[0])
            type = branch[1]
            value = branch[2]
            parent = branch[3]
            left = branch[4]
            right = branch[5].strip()
            branch = Node(id,type,value,parent,left,right)
            pathList.append(branch)

        #sort each node by its id
        pathList.sort(key=lambda node: node.id)
        
        #create tree
        #if the left child is not a leaf, add the left child to the root
        #vice versa for right
        for i in range (len(pathList)):
            node = pathList[i]
            leftChild = pathList[i].left
            rightChild = pathList[i].right
            if node.left != '':
                node.left = pathList[int(leftChild)]
            if node.right != '':
                node.right = pathList[int(rightChild)]
        
        return pathList
    
    #just exit the program if the file is faulty
    except FileNotFoundError:
        print("Your database file is invalid!")
        sys.exit()


#desc: the main method the game is run on. will loop until an answer is found, there are no more questions, or there
#      are no more answers. List will be updated in the last two cases locally.
#pre : -parameter sortedList is assumed to be a sorted list (by Node.id)
#post: none
def query(sortedList):
    #start the game with needed initial values
    #sortedList is put into pathList since pathList will be modified
    pathList = sortedList
    isContinuing = True
    root = pathList[0]

    #begin loop
    while (isContinuing):
        #if current node is a question, ask the question
        if root.type == "question":
            userin = input("{0} (y/n): ".format(root.value)).lower()
            #if answer is y and if there is a left child, current node = left child
            #if there is no children, append an answer to the end
            if userin == "y":
                if root.left != None:
                    root = root.left
                else:
                    print("\nI've run out of things to guess!")
                    newAnswer = input("Provide a new thing to add to my knowledge: ")
                    newIndex = len(pathList)
                    pathList.append(Node(newIndex,"answer", newAnswer, root.id, None, None))
                    pathList[root.id].left = pathList[-1]
            #if answer is n and if there is a right child, current node = right child
            #if there is no children, append an answer to the end
            elif userin == "n":
                if root.right != None:
                    root = root.right
                else: 
                    print("\nI've run out of things to guess!")
                    newAnswer = input("Provide a new thing to add to my knowledge: ")
                    newIndex = len(pathList)
                    pathList.append(Node(newIndex,"answer", newAnswer, root.id, None, None))
                    pathList[root.id].right = pathList[-1]
            #deal with invalid input 
            else:
                print("Invalid input.")
                userin = input("{0} (y/n): ".format(root.value)).lower()

        #if the current node is an answer, ask "is it __?"
        else:
            userin = input("Is it a(n) {0}? (y/n): ".format(root.value)).lower()
            #if yes, end round
            if userin == "y":
                print("\nI win! Better luck next time.")
                break
            #if no, add a new question either on the end of yes or no.
            #the answer that the game guessed will be the respective child of the new question
            elif userin == "n":
                print("\nYou've stumped me! Help me learn how to beat you next time.")
                newQuestion = input("Provide a new yes/no question: ")
                userin = input("Would a(n) {0} be associated with a yes or a no to this question? ".format(root.value))
                if userin == "y":
                    newIndex = len(pathList)
                    newAnswer = root.value
                    pathList[root.id].type = "question"
                    pathList[root.id].value = newQuestion
                    pathList.append(Node(newIndex, "answer", newAnswer, root.id, None, None))
                    pathList[root.id].left = pathList[-1]
                    break
                elif userin == "n":
                    newIndex = len(pathList)
                    newAnswer = root.value
                    pathList[root.id].type = "question"
                    pathList[root.id].value = newQuestion
                    pathList.append(Node(newIndex, "answer", newAnswer, root.id, None, None))
                    pathList[root.id].right = pathList[-1]
                    break
                #deal with invalid input
                else:
                    print("Invalid input.")
                    userin = input("Would a(n) {0} be associated with a yes or a no to this question? ".format(root.value))
        
    #ask if the player wants to go for another round
    playAgain = input("Play again? (y/n): ").lower()
    root = pathList[0]
    if playAgain == "n":
        print("I had fun! Let's play again sometime.")
    elif playAgain != "y":
        print("Invalid input. I'll just stop it anyway.")
    else:
        query(pathList)
                        

#desc: initializes a list with user inputed first question as the root of the tree.
#pre : -this is only run if there are no arguments
#post: none
def userinDatabase():
    pathList = []
    counter = 0
    userin = input("Provide First Question: ")
    pathList.append(Node(counter,"question",userin, None, None, None))
    query(pathList)


if __name__ == "__main__":
    #if a database is provided, take this path
    if len(sys.argv) == 2:
        pathList = []
        pathList = fileRead()
        print("Starting the 20 Questions Game.")
        print("Thanks for passing me my database!")
        query(pathList)
    #try running the program again if there are too many arguments
    elif len(sys.argv) > 2:
        print("Too many arguments!")
    #if no arguments, start from scratch
    else:
        print("Starting the 20 Questions Game.")
        userinDatabase()