
IMG_PATH = 'data/img/'
SND_PATH = 'data/snd/'
CUSTOM_IMG_PATH = IMG_PATH + 'custom/'
CUSTOM_SND_PATH = SND_PATH + 'custom/'
TEMP_IMG_PATH = IMG_PATH + 'temp/'
TEMP_SND_PATH = SND_PATH + 'temp/'
CUSTOM_CARDS_FILE = 'card/custom_cards.py'
CUSTOM_CARDS_HEADER = 'from . import card_base\n'
SAVE_DATA_PATH = 'data/save/'
SAVE_DATA_FILE = SAVE_DATA_PATH + 'save.json'
TEST_CARD_FILE = 'node/tester/testing_card.py'
TEST_CARD_HEADER = 'from card import card_base\n'
INFO_SHEET_FILE = 'data/node/sheet_info.json'

BASE_NAMES = (
    'michael', 'dom', 'jack', 'mary', 'daniel', 'emily', 'gambling boi', 'mom', 'dad',
    'aunt peg', 'uncle john', 'kristen', 'joe', 'robber', 'ninja', 'item frenzy', 'mustard stain', 'gold coins',
    'gold', 'max the dog', 'basil the dog', 'copy cat', 'racoon', 'fox', 'cow', 'shark', 'fish',
    'pelican', 'lucky duck', 'lady bug', 'mosquito', 'snail', 'dragon', 'clam', 'pearl', 'uphalump',
    'flu', 'cactus', 'poison ivy', 'rose', 'mr. squash', 'mrs. squash', 'ghost', 'fishing pole', 'invisibility cloak',
    'last turn pass', 'detergent', 'treasure chest', 'speed boost potion', 'fertilizer', 'mirror', 'sword', 'spell trap', 'item leech',
    'curse', 'treasure curse', 'bronze', 'negative zone', 'item hex', 'luck', 'fishing trip', 'bath tub', 'boomerang',
    'future orb', 'knife', 'magic wand', 'lucky coin', 'sapling', 'vines', 'zombie', 'jumble', 'demon water glass',
    'succosecc', 'sunflower', 'lemon lord', 'wizard', 'haunted oak', 'spell reverse', 'sunny day', 'garden', 'desert',
    'fools gold', 'graveyard', 'city', 'wind gust', 'sunglasses', 'metal detector', 'sand storm', 'mummy', 'mummys curse',
    'pig', 'corn', 'harvest', 'golden egg', 'bear', 'big rock', 'unlucky coin', 'trap', 'hunting season',
    'stardust', 'water lily', 'torpedo', 'bat', 'sky flower', 'kite', 'balloon', 'north wind', 'garden snake',
    'flower pot', 'farm', 'forest', 'water', 'sky', 'office fern', 'parade', 'camel', 'rattle snake',
    'tumble weed', 'watering can', 'magic bean', 'the void', 'bug net', 'big sand worm', 'lost palm tree', 'seaweed', 'scuba baby'
)

CONSTANTS = {
    'width': 1024,
    'height': 576,
    'screen_size': (1024, 576),
    'center': (1024 // 2, 576 // 2),
    'cw': 375 // 10,
    'ch': 525 // 10,
    'mini_card_size': (375 // 10, 525 // 10),
    'card_width': 375,
    'card_height': 525,
    'card_size': (375, 525),
    'fps': 30
}

CONFIRMATION_CODE = 'thisisthecardgameserver'

def get_sorted_names_dict():
    names = sorted(BASE_NAMES)
    
    out = {
        'A-D': {n: None for n in names if n[0] in 'abcd'},
        'E-H': {n: None for n in names if n[0] in 'efgh'},
        'I-L': {n: None for n in names if n[0] in 'ijkl'},
        'M-P': {n: None for n in names if n[0] in 'mnop'},
        'Q-T': {n: None for n in names if n[0] in 'qrst'},
        'U-Z': {n: None for n in names if n[0] in 'uvwxyz'}
    }
    
    return out
    
SORTED_NAMES_DICT = get_sorted_names_dict()
    
TAGS_DICT = {
    'biomes': {
        'city': None,
        'desert': None,
        'forest': None,
        'farm': None,
        'garden': None,
        'graveyard': None,
        'sky': None,
        'water': None
    },
    'descriptors': {
        'animal': None,
        'bug': None,
        'dog': None,
        'human': None,
        'monster': None,
        'plant': None
    }
    
}
    
TYPES_DICT = {
    'event': None,
    'item': None,
    'landscape': None,
    'play': None,
    'spell': None,
    'treasure': None,
}

DECKS_DICT = {
    'active_spells': None,
    'items': None,
    'landscapes': None,
    'played': None,
    'spells': None,
    'treasure': None,
    'unplayed': None
}

REQUESTS_DICT = {
    'flip': None,
    'roll': None,
    'select': None,
    'og': None
}
        
        
        
        
