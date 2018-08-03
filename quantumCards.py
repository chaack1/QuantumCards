from pyquil.quil import Program
from pyquil.gates import STANDARD_GATES as sg
from pyquil.gates import MEASURE
sg['MEASURE'] = MEASURE
from pyquil.api import QVMConnection
import random as rd
import itertools as it
from math import pi

class Game(object):
    """
    Holds the players, the gate-deck.
    Manages turns, checking up on player state.
    Instantiates with certain paramaters: how many players, how many bits per player, how is the game started, etc.
    """
    deckContents = [['H',4],['CNOT',2],['X',2],['SWAP',2],['MEASURE',2]]
    numPlayers = 2
    numOfBits = 4 #number of bits, to be divided amongst the players.
    start = '0' #What operation to start each bit with
    deal = 'Random' #'Random' or 'Identical'
    longLineSuppress = True #Supress wavefunctions and state probabilites if more than 4 bits. 

    def __init__(self):

        if self.numOfBits % self.numPlayers != 0:
            raise ValueError("numOfBits must be evenly divisible by numPlayers")

        self.theGame = Program()

        #Create the deck
        self.deck = self.makeDeck()
        self.handSize = int(len(self.deck)/self.numPlayers)

        #Initialize the bits to be used in the game.
        if self.start == 'H': #Start every player with every state being equally likely. 
            for bit in range(self.numOfBits):
                self.theGame.inst(sg['H'](bit))
        elif self.start == '0': #Start every player with all bits zero.
            for bit in range(self.numOfBits):
                self.theGame.inst(sg['MEASURE'](bit,0))
        elif self.start == '1': #Start every player with all bits one.
            for bit in range(self.numOfBits):
                self.theGame.inst(sg['X'](bit))
        elif self.start == 'Random': #Start every player with all bits having a random gate applied from the deck.
            for bit in range(self.numOfBits):
                self.theGame.inst(rd.choice(self.deck)(bit))
        
        #Initialize the players
        self.players = [Player(i+1,self.deck,self.handSize) for i in range(self.numPlayers)]

        #Start the Game!
        self.playGame()
    
    def makeDeck(self):
        """Creates the deck for the game based on deckContents"""
        deckList = self.deckContents.copy()
        for i in range(len(deckList)):
            if len(deckList[i]) == 2: #No parameters for the gate
                deckList[i] = [sg[deckList[i][0]],deckList[i][1]]
            elif len(deckList[i]) == 3: #1 parameter for the gate
                deckList[i] = [sg[deckList[i][0]](deckList[i][1]),deckList[i][2]]
        deck = []
        for g,num in deckList:
            deck += [g]*num
        
        if (self.deal == 'Random'):
            if (len(deck) % self.numPlayers != 0):
                raise ValueError("Length of deck must be evenly divisible by numPlayers")
            rd.shuffle(deck)
        return deck
    
    def playGame(self):
        """Starts the game"""
        while self.playerHasCards():
            for player in self.players:
                self.displayState()
                self.theGame.inst(player.turn())
        self.theGame.measure_all()
        #print(self.theGame)
        qvm = QVMConnection()
        results = qvm.run(self.theGame)
        resultsRev = results[0][:]
        resultsRev.reverse() #So the printed results are in the same order as everything else.
        print('The bits were measured as: ',resultsRev)
        winners = self.checkWinner(results[0])
        if len(winners) != 1:
            print("It's a draw!")
        else:
            print("Player " + str(winners[0]+1) + " wins!")

    def playerHasCards(self):
        """Returns true iff there exists a player with a non-empty hand"""
        for player in self.players:
            if player.hand != []:
                return True
        return False
    
    def displayState(self):
        qvm = QVMConnection()
        wf = qvm.wavefunction(self.theGame)
        probs = wf.probabilities()
        if self.numOfBits <= 4 or not self.longLineSuppress: #Avoids printing long wavefunctions.
            print('Wavefunction:',wf)
            print('State Probabilities:',[round(i,2) for i in probs])
        print('Win Probabilites:', self.winProbabilities(probs))
    
    def winProbabilities(self, probs):
        """Displays the probabilites that each player will win based on the current wavefunction"""
        winProbs = [0 for i in range(self.numPlayers + 1)] #the last entry is probability of draw
        for prob,bits in zip(probs,it.product([0,1],repeat=self.numOfBits)):
            winners = self.checkWinner(bits)
            if len(winners) != 1:
                winProbs[-1] += prob
            else:
                winProbs[winners[0]] += prob
        winProbs = [round(i,3) for i in winProbs]
        return winProbs

    def checkWinner(self,bitList):
        #grouper method from https://docs.python.org/3/library/itertools.html#itertools-recipes
        def grouper(iterable, n, fillvalue=None):
            "Collect data into fixed-length chunks or blocks"
            args = [iter(iterable)] * n
            return it.zip_longest(*args, fillvalue=fillvalue)
        totals = [0 for i in range(self.numPlayers)]
        groupedBits = list(grouper(bitList,int(self.numOfBits/self.numPlayers)))
        for groupedBitsIndex in range(len(groupedBits)):
            totals[groupedBitsIndex] = sum(groupedBits[groupedBitsIndex])
        
        maxScore = max(totals)
        winners = []
        while maxScore in totals:
            winners.append(totals.index(maxScore))
            totals.remove(maxScore)
        return winners
        
class Player(object):
    #Has a hand, made of qbits
    #Can play cards against other players or themselfe to change the state of the hand.
    def __init__(self,playerNum,deck,handSize):
        self.playerNum = str(playerNum)
        self.hand = []
        if Game.deal == 'Random':
            for i in range(handSize):
                self.hand.append(deck.pop())
        elif Game.deal == 'Identical':
            self.hand = deck.copy()
        else:
            raise ValueError("'" + Game.deal +"' is not a valid drawStyle.")
    
    def turn(self):
        print('Player' + self.playerNum + "'s turn!")
        print('Your hand: ', self.handList())
        gateStr = input("Pick a gate:") #Player gives an input, H 0 for 1 qbit gate, CNOT
        gateInfo = gateStr.split()
        inputValid, inputInfo = self.inputCheck(gateInfo)
        
        if not inputValid:
            print(inputInfo)
            return self.turn()

        ret = None
        for gate in self.hand:
            try: #What if gates take more than one thing?
                if gateInfo[0] == str(gate(0)).split()[0]:
                    if gateInfo[0] == 'MEASURE':
                        ret = gate(int(gateInfo[1]),0) #I think there is a bug in the api. Looking for address in measure when it shouldn't?
                    else:
                        ret = gate(int(gateInfo[1]))     
            except:
                if gateInfo[0] == str(gate(0,1)).split()[0]:
                    ret = gate(int(gateInfo[1]),int(gateInfo[2]))
            if ret != None:
                self.hand.remove(gate)
                break
        if gateInfo[0] == 'MEASURE': #The string of MEASURE includes a superfluous [0] at the end that isn't relevant to the game.
            print('Player ' + self.playerNum + ' played ' + str(ret).split()[0] +' '+ str(ret).split()[1])
        else:
            print('Player ' + self.playerNum + ' played ', ret)
        return ret

    def inputCheck(self,gateInfo):
        """
        Checks if input is valid. An input is invalid if:
        Not in the format 'GATE NUM NUM'
        Not in the hand
        Improper num of bits for the gate
        qbits aren't distinct
        Bits are too high
        Parameters:
        gateInfo: list of str, the split() list of the input
        Returns:
        isValid : bool, Ture if the input is valid
        error : str, if invalid, info on its invalidity.
        """
        #Check if not in the hand, or if input is empty.
        try:
            if gateInfo[0] not in self.handList():
                return False, gateInfo[0] + " is not in your hand."
        except:
            return False, "Type something!!"

        #Check that the number of bits given equals the number of args the gate takes.
        for gate in [sg[entry[0]] for entry in Game.deckContents]:
            for i in range(3):
                try:
                    gateStr = str(gate(*(j for j in range(i+1)))).split()[0] 
                    numArgs = i+1
                    break
                except:
                   continue
                return False, 'Unknown Error in parsing input. Try Again'
            try:
                if gateInfo[0] == gateStr:
                    if len(gateInfo[1:]) != numArgs:
                        raise ValueError('number of bits does not match number of args')
            except:
                return False, 'The number of bits given for ' + gateStr + ' must be ' + str(numArgs) +'.'
        
        #Each qbit in the argument must be unique:
        for i in gateInfo[1:]:
            if gateInfo[1:].count(i) != 1:
                return False, 'Each bit given must have distinct indices.'
                            
        #Check to see if nums are actually nums between 0 and numOfBits.
        for num in gateInfo[1:]:
            try:
                if int(num) > Game.numOfBits -1:
                    raise ValueError("Incorrect num of bits")
            except:
                return False, num + " must be an integer between 0 and " + str(Game.numOfBits - 1)
        
        return True, ''

    def handList(self):
        """Returns the gates in the player's hand as a list"""
        hStr = ''
        for gate in self.hand:
            for i in range(3):
                try:
                    hStr += str(gate(*(j for j in range(i)))).split()[0] + ' '
                    break
                except:
                    continue
        return hStr.split()

if __name__ == '__main__':
    Game()

#Possible Additions:
#Add a way for the user add defined gates to the game.

#A help mode for players, to understand what the gates actually do.
#i.e the player types 'Help GATE' for info on what GATE does.

#Difficulty modes, that adjust what info about the states are given to the players.
#Wavefunction/Probabilites etc.

#A way for the player to give parameters to parameterized gates.
#Right now the gates are given parameters when the game is started.
#I'm concerned that giving the players this ability will either be really confusing or OP.
