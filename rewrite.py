import json
import cards

data = cards.cards

for deck in data:
    for name in data[deck]:
        r, init, types = data[deck][name]
        data[deck][name] = {'weight': r, 'init': init.__name__}

with open('save/cards.json', 'w') as f:
    json.dump(data, f, indent=4)