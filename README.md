# Card-Game
Table top card game with local wireless play.

To play, make sure to have pygame installed. Run the client.py file from command prompt to start.
To start a local wireless game, click "single player" on the main menu
To join a local wireless game click "find game" on the main menu

Controls:
  press "S" to start a game (when playing in wireless mode, you will only be able to start a game if at least one other person has joined the game)
  press "R" to restart or start a new game
  
Cards:
  while playing a game, any card that is shown on screen can be blown up to allow you to read what it does.
  Hover your mouse over the card and hold "alt" to display the card in the middle of the screen
  
  The title of the card is displayed at the top
  Next is the picture
  Below the picture is the description.
  Often times a card will have a bonus effect which can be activated by satisfying a condition that is outlined on the card
  On the bottom is the type of card.
  
Card Types:
  Event cards:
    Event cards are cards that have an overarching effect on the game.
    Sometimes they grant a special bonus at the end of the round
    Other times they mix things up at the beginning of the round
    The event card effects all players, so be sure to take a look at it at the beginning of the game to see how you could capitalize on it.
    
  Item cards:
    Items are cards that give you special advantages during the game.
    In general, items can be used at any point during the game
    Some items need specific conditions in order to activate. When used they will go into your "equipped" pane (discussed later)
    
  Spell cards:
    spell cards are cards that when casted on a player, will affect them until either then end of the round, or they get removed somehow.
    Often time, spells will take effect at the end of your turn
    Spells that you can cast will appear in your "items" pane
    To cast a spell, click on the spell, then select the player that you wish to cast the spell on from the selection pane.
    Spells that have been casted on you will appear in the "spells" pane
    Spells in your "spells" pane will activate automatically when their conditions are met
    
  Treasure cards:
    treasure cards are cards that you have to get super lucky to obtain.
    In order to get a treasure card, you must meet certain criteria outlined on some cards.
    If you can hold on to treasures until the end of the game, the cards will take effect and you will often receive a large amount of points
    
  Landscape cards:
    Landscape cards provide a bonus for playing any cards that correspond to them.
    Cards played while the corresponding landscape is in your position will be played twice.
    check the bottom box on cards in your sequence to see which cards correspond to your landscape
    
  Other:
    any other cards that don't fall under the above types are cards that are played regularly in sequences.

Screen:
  Selection pane (blue pane on right side of screen):
    Cards that appear here need to be selected by clicking on them
    Cards will appear here in the draft phase of the game (discussed later) or during a game, often triggered by a card you played
    
  Sequence pane:
    Cards that appear here are cards that are "in your sequence" The order they appear is the order you draft them in.
    Cards here cannot be directly interacted with.
    The top card is the card that will be played next
    
  Active card:
    Your active card is the card that is currently in control of your actions.
    If cards suddenly appear in your selection pane, make sure to look at your active card to check what prompted the selection and what will happen next.
    
  Items pane:
    Pane that holds any items or spells that are currently in your hand.
    Items can be selected and used by clicking on them.
    If you click and nothing happens, that item or spell cannot be used at the moment.
    If an item card that you use prompts a selection and you decide you don't want to use the item any more, press 'X' to cancel the selection
    Sometimes when you use an item, depending on the item it will be added to your "equipped" pane.
  
  Equipped pane:
    Equipped items are items that cannot be used at the immediate moment but will take the next available opportunity to activate. 
    To unequip an item, just click it and it will be sent back to your items pane
    
  Spells pane:
    This pane displays spells that have been casted on you.
    This pane cannot be interacted with.
  
  Treasure pane:
    This pane shows you any treasures you have collected.
    Treasures cannot be interacted with, with the exception of gold coins which can be clicked on to draw a new item.
    
  Score:
    The leader board and scores will appear in the top left corner of the screen.
    
  Other players:
    Your opponents will appear across the middle of your screen
    The main pane that appears is their sequence
    When they play a new card, it will become visible to you under their name.
    Hovering your mouse over an opponent’s sequence will display more info about the cards they have.
    On the far left you will be able to see the landscape card they currently have
    On the close left, you will be able to see any spells that are currently casted on them
    On the close right you will be able to see any items that they previously used

Rules:
Phase 1:
  when the game starts you will receive items and spells that get added to the respective panes
  You will also receive a landscape card which can be viewed as discussed in "other players" above
  
  Cards will appear in the selection pane on the right
  Each player will select one card which will be added to their sequence
  Once each player has selected a card, the remaining cards will rotate to the next player and another selection will be made
  
  This happens until all cards have been selected.
  
Phase 2:
  Once all selections have been made, the game starts.
  To advance the turn, player a card from your sequence.
  You will not be able to play a card if it is not your turn
  
  Once all players have played all of the cards in their sequence the game ends
  
  The player with the highest score (displayed in top left) is the winner






























