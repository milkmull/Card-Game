import inspect
import importlib

import data.save

from . import card_base
from . import base_cards
from . import extra_cards
from . import custom_cards

def load_custom_cards():
    importlib.reload(custom_cards)

def predicate(obj):
    return inspect.isclass(obj) and issubclass(obj, card_base.Card) and not obj is card_base.Card
    
def get_vote_card(game):
    return extra_cards.VoteCard(game)
    
def get_base_card_data():
    data = {}
    for name, cls in inspect.getmembers(base_cards, predicate):
        if cls.type not in data:
            data[cls.type] = {}
        data[cls.type][cls.name] = cls
    return data

def get_custom_card_data():
    data = {}
    for name, cls in inspect.getmembers(custom_cards, predicate):
        if cls.type not in data:
            data[cls.type] = {}
        data[cls.type][cls.name] = cls
    return data
    
def get_playable_card_data():
    data = {}
    
    for cls in card_base.Card.get_subclasses():
        if cls.type not in data:
            data[cls.type] = {}
        data[cls.type][cls.name] = cls
    
    return data
    
    
    
    
    
    