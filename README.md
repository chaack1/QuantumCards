# QuantumCards : A quant-fun game for 2+ players.
QuantumCards is a game that uses lets players use their knowledge of quantum mechanics(!) to maximize thier chance of winning the game.

## Basic rules of the game:
There are a number of players each given a number of qbits, and a set of quantum gates to manipulate said qubits. Players take turns playing the gates in their hands on any qbit(s) on the table, be it one of their own or one of their opponents'. At the end of the game, the state of the qbits on the table are measured, and whomever's bits add up to the highest number wins. 

## Requirments
Python 3

pyquil, https://github.com/rigetticomputing/pyquil

## Playing the game
After you download the quantumCards.py script, you can run it like a regular script, or import it.
Running it like a regular script will allow you to launch right into a game with the default settings.
Importing it will allow you to change some settings in the game, like the number of players, before you launch it.

If you import the game, you can launch it by typeing in the interpereter, with quantumCards.py in the `sys.path`:
```python
import quantumCards
quantumCards.Game()
```

When the game starts, you'll see something in the output like:
```
Wavefunction: (1+0j)|0000>
State Probabilities: [1. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.]
Win Probabilites: [0.0, 0.0, 1.0]
Player 1's turn!
Your hand:  ['H', 'CNOT', 'X', 'MEASURE, RX(pi)']
Pick a gate:
```
The state probabilities are given in the standard order, i.e 0000 0001 0010 0011 ... 1111.
In both the wavefunction and the state probabilites, the players bits read from right to left. For example, in a two player game where both players get two bits, the bitstring '0011' means player 1 has bits in state 11, and player 2 has bits in state 00.
The win probabilites give the probabilites of winning the game for players 1 through player N, followed by the probability of a tie.

To play a one-qbit gate, just type the name of the gate, and the bit you play it on seperated by a space, like:
```
X 0
```
For a multi-qubit gate, again just type the name of the gate and the bits they act on seperated by spaces, like:
```
CNOT 0 2
```
For a gate with a parameter, just type it like a normal gate:
```
RX(pi) 0
```

Then keep playing gates until each player has no more cards. At the end of the game, the state of the system is measured, and a winner is whoever had the highest number of bits in state 1.

## Adjusting the game.
Before you launch the game with `Game()` you can make a few adjustments to how the game will be played by changing the values of the Game class's attributes. For example, after importing quantumCards.py
```python
from math import pi
quantumCards.Game.numPlayers = 3 
#Default 2

quantumCards.Game.numOfBits = 6
#Default 4. Number of bits must be evenly divisable by numPlayers.

quantumCards.Game.start = '1' 
#Default '0'. 
Can be '0','1','H', or 'Random'. 
'0' will start all bits in state 0, '1' will start all bits in state 1, 'H' will apply the H gate to each bit, and 'Random' will apply random gates that are in the deck to each bit.

quantumCards.Game.deal = 'Identical'
#Default 'Random'. If 'Random', each player gets a random hand from the deck. 
If 'Identical', each player gets an exact copy of the deck in their hand.

quantumCards.Game.deckContents = [['H',5],['RX',pi,2],['MEASURE',1]]
#Default [['H',4],['CNOT',2],['X',2],['SWAP',2],['MEASURE',2]]. 
Each entry gives a string representation of gates from pyquil.gates.STANDARD_GATES, along with MEASURE. 
Regular gates also give the number of that kind of gate in the deck. 
Parameterized gates give a parameter for the gate, and then the number of that kind of gate in the deck. 
If deal is 'Random' the number of gates in the deck must be divisible by the number of players.

quantumCards.Game.longLineSuppress = False
#Defualt True. 
If there are more than 4 qbits in the game, then output of the wavefunction and state probabilities will be suppressed if True. 
Keep in mind that the number of terms in the general wavefunction will by 2^n the number of bits, so be careful if you turn this off with a large number bits.

#After the desired settings are adjusted, start the game!
quantumCards.Game()
```

## Possible Future Additions
* A way for the user to add defined gates.
* A way for players to give parameters to parameterized gates.
* Difficulty modes that hide information about the wavefunction, or introduce noise to the measurements.
* Variations on the base game, like including extra qbits owned by noone that can give extra points to players who manipulate them properly. 
