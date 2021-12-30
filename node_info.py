


info = {

'start': 
{
'body':
'''Represents the start of the main function. When a card is played, this is the first thing that will be run.''',
-1: 'flow'
},

'if': 
{
'body':
'''If the boolean argument is true, the split path is run before returning to the main flow. If it is false, the main flow is continued.''',
1: 'bool',
2: 'flow',
-1: 'split',
-2: 'flow'
},

'elif': 
{
'body':
'''Can only be placed after the flow port on an If or Elif block. If the If block is True, this block will be skipped. If it is False, this block will be evaluated. If the boolean value is true, the split path is run before returning to the main flow. If it is false, the main flow is continued.''',
1: 'bool',
2: 'flow',
-1: 'split',
-2: 'flow'
},

'else': 
{
'body':
'''Can only be placed after the flow port on an If or Elif block. If the previous If or Elif boolean values are False, the split path is run before returning to the main flow. If any of the If or Elif statements are True, the split path is skipped and the main flow is continued.''',
1: 'flow',
-1: 'split',
-2: 'flow'
},

'bool': 
{
'body':
'''Bool values are either True or False. Type in "T" or "t" for True, and "F" or "f" for false.''',
-1: 'bool',
},

'num': 
{
'body':
'''Just a number, floating points not allowed! >:(''',
-1: 'num',
},

'string': 
{
'body':
'''A string of characters. These are often used to check names and tags of cards.''',
-1: 'string',
},

'and': 
{
'body':
'''Takes two boolean inputs. Will output True if both inputs are True, otherwise False.''',
1: 'a',
2: 'b',
-1: 'a and b'
},

'or': 
{
'body':
'''Takes two boolean inputs. Will output True if one or both inputs are True. If both are False, it will output False.''',
1: 'a',
2: 'b',
-1: 'a or b'
},

'not': 
{
'body':
'''Takes one boolean input. Will output True if input is False, and False if input is True.''',
1: 'a',
-1: 'not a'
},

'equal': 
{
'body':
'''Takes two inputs. Will output True if both are equal, otherwise False. Double click this node to switch the input types. Can compare numbers, strings, players, and cards.''',
1: 'a',
2: 'b',
-1: 'a == b'
},

'greater': 
{
'body':
'''Takes two numerical inputs. Will output True if a is greater than b, otherwise False.''',
1: 'a',
2: 'b',
-1: 'a > b'
},

'less': 
{
'body':
'''Takes two numerical inputs. Will output True if a is less than b, otherwise False.''',
1: 'a',
2: 'b',
-1: 'a < b'
},

'add': 
{
'body':
'''Takes two numerical inputs and outputs their sum.''',
1: 'a',
2: 'b',
-1: 'a + b'
},

'incriment': 
{
'body':
'''Takes a numerical input and adds 1.''',
1: 'a',
-1: 'a + 1'
},

'subtract': 
{
'body':
'''Takes two numerical inputs and outputs their difference.''',
1: 'a',
2: 'b',
-1: 'a - b'
},

'multiply': 
{
'body':
'''Takes two numerical inputs and outputs their product.''',
1: 'a',
2: 'b',
-1: 'a * b'
},

'divide': 
{
'body':
'''Takes two numerical inputs and outputs their quotient.''',
1: 'a',
2: 'b',
-1: 'a / b'
},

'negate': 
{
'body':
'''Takes one numerical input and outputs its inverse value.''',
1: 'a',
-1: '-a'
},

'exists': 
{
'body':
'''tkes a player or card input. If the input is not a None value, the output is True, otherwise False.''',
1: 'player/card',
-1: 'bool'
},

'for': 
{
'body':
'''Takes in a sequence of values. Each value will be output at the top port. The split path will run once for each value in the sequence. After completion, the main flow will continue. The output values are only usable within the split path.''',
1: 'sequence',
2: 'flow',
-1: 'value',
-2: 'split',
-3: 'flow'
},

'break': 
{
'body':
'''Only usable within the split path of a For block. When it is hit, this node will cause the split path of the For block to end and the main flow will continue.''',
1: 'flow',
},

'continue': 
{
'body':
'''Only usable within the split path of a For block. When it is hit, this node will cause the next value to be pulled out of the sequence and the split path will be started from the top.''',
1: 'flow',
},

'range': 
{
'body':
'''Generates a sequence of numerical values. The first input represents the start value, the second input represents the stop value.''',
1: 'start',
2: 'stop',
-1: 'sequence',
},

'all players': 
{
'body':
'''Outputs a sequence containing every player.''',
-1: 'all players',
},

'opponents': 
{
'body':
'''Outputs a sequence containing every player except the player who is using the card.''',
-1: 'opponents',
},

'opponents with points': 
{
'body':
'''Players with 0 points cannot be stolen from. This node outputs a sequence containing every player except the player who is using the card and any player who has 0 points.''',
-1: 'opponents',
},

'player': 
{
'body':
'''This node outputs the player who played this card.''',
-1: 'player'
},

'length': 
{
'body':
'''This node outputs the length of the given sequence, or how many values are in the sequence.''',
1: 'sequence',
-1: 'num'
},

'merge lists': 
{
'body':
'''Merges two sequences into one. Both connected sequences must contain the same type of values.''',
1: 'sequence',
2: 'sequence',
-1: 'sequence'
},

'merge lists in place': 
{
'body':
'''adds all values from sequence2 to sequence1. Both sequences must contain the same type of values. This is mainly used in the get selection function to add cards or players to the sequence that the player will choose from.''',
1: 'sequence2',
2: 'sequence1',
3: 'flow',
-1: 'flow'
},

'contains': 
{
'body':
'''Takes in a player or card value and a sequence. Outputs True if the value is in the sequence, otherwise False.''',
1: 'player/card',
2: 'sequence',
-1: 'bool'
},

'get played': 
{
'body':
'''Takes a player as input, returns a sequence containing the cards they have played so far.''',
1: 'player',
-1: 'played cards'
},

'get unplayed': 
{
'body':
'''Takes a player as input, returns a sequence containing the cards in their sequence that have not yet been played.''',
1: 'player',
-1: 'unplayed cards'
},

'get active spells': 
{
'body':
'''Takes a player as input, returns a sequence containing the spell cards that are currently affecting them.''',
1: 'player',
-1: 'active spells'
},

'get items': 
{
'body':
'''Takes a player as input, returns a sequence containing the item cards the currently have. This includes any unactivated equipment cards.''',
1: 'player',
-1: 'items'
},

'has tag': 
{
'body':
'''Takes a card and string as input. Output is True if one of the cards tags matches with the string, otherwise False.''',
1: 'tag',
2: 'card',
-1: 'has tag'
},

'has name': 
{
'body':
'''Takes a card and string as input. Output is True if the cards title matches with the string, otherwise False.''',
1: 'name',
2: 'card',
-1: 'has name'
},

'tag filter': 
{
'body':
'''Takes in a sequence of cards and a string. The output will be a sequence of cards taken from the input sequence, but only one of their tags matches with the string input. If the input boolean is True, this card will also be filtered out if it happens to be in the input sequence.''',
1: 'string',
2: 'self?',
3: 'cards',
-1: 'cards'
},

'tag filter': 
{
'body':
'''Takes in a sequence of cards and a string. The output will be the number of cards in the input sequence whos tags match with the string input. If the input boolean is True, this card will also be filtered out if it happens to be in the input sequence.''',
1: 'string',
2: 'self?',
3: 'cards',
-1: 'num'
},

'gain': 
{
'body':
'''Takes in a player, and number. The player will gain the number of points specified.''',
1: 'points',
2: 'player',
3: 'flow',
-1: 'flow'
},

'lose': 
{
'body':
'''Takes in a player, and number. The player will lose the number of points specified. This number should be positive.''',
1: 'points',
2: 'player',
3: 'flow',
-1: 'flow'
},

'steal': 
{
'body':
'''Takes in two players, and number. The first player will steal the number of points specified from the target player.''',
1: 'points',
2: 'player',
3: 'target',
4: 'flow',
-1: 'flow'
},

'start flip': 
{
'body':
'''Initiates a coin flip for the player who played this card. In order to complete the coin flip process, a flip node must be present.''',
1: 'flow'
},

'flip': 
{
'body':
'''This function is run after the player flips a coin. A coin flip can be triggered with a start flip node. If no start flip node is present, this function will not run. The coin flip result is returned as a boolean value. True if the player flipped heads, and False if tails.''',
-1: 'coin',
-2: 'flow'
},

'start roll': 
{
'body':
'''Initiates a dice roll for the player who played this card. In order to complete the dice roll process, a roll node must be present.''',
1: 'flow'
},

'roll': 
{
'body':
'''This function is run after the player rolls the dice. A dice roll can be triggered with a start roll node. If no start roll node is present, this function will not run. The dice roll result is returned as a numeric value: 1-6.''',
-1: 'roll',
-2: 'flow'
},

'start select': 
{
'body':
'''Initiates a selection for the player who played this card. In order to complete the selection process, get selection and select nodes must both be present.''',
1: 'flow'
},

'get selection': 
{
'body':
'''When the player is prompted to make a selection, this function is called to give a sequence for the player to select from. Add to the selection sequence using the 'merge list in place'. Double click to change between a card sequence and a player sequence. In order for this node to run, a "start select" node and a 'select' node must both be present.''',
-1: 'selection',
-2: 'flow'
},

'select': 
{
'body':
'''This function is run after the player makes a selection. It will return the number of cards or players the player has selected and the last selected card or player. In order for this node to run, a 'start select' node and a 'select' node must both be present.''',
-1: 'number selected',
-2: 'last selected',
-3: 'flow'
},

'start ongoing': 
{
'body':
'''This node initiates an ongoing task. While in ongoing, the card will wait for a specific event to occur, when it does, the card will execute some task. In order for this node to run, an 'initiate ongoing' node and an 'ongoing' node must both be present.''',
1: 'flow',
},

'initiate ongoing': 
{
'body':
'''This node runs before an ongoing task starts. This is where you should use the 'add log type' node to set the type of log that will trigger your ongoing function. In order for this node to run, an 'start ongoing' node and an 'ongoing' node must both be present.''',
1: 'flow',
},

}