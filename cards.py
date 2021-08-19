from func import *

cards = {

        'play': {

                    'michael': (1, Michael, ('human',)),

                    'dom': (3, Dom, ('human',)),
                    
                    'jack': (1, Jack, ('human',)),

                    'mary': (3, Mary, ('human',)),
                    
                    'daniel': (2, Daniel, ('human',)),

                    'emily': (2, Emily, ('human',)),

                    'gambling boi': (3, GamblingBoi, ('human', 'city')),

                    'mom': (2, Mom, ('human',)),

                    'dad': (1, Dad, ('human',)),
                    
                    'aunt peg': (2, AuntPeg, ('human',)),
                    
                    'uncle john': (1, UncleJohn, ('human',)),
                    
                    'kristen': (1, Kristen, ('human',)),
                    
                    'joe': (1, Joe, ('human',)),
                    
                    'robber': (3, Robber, ('human', 'city')),
                    
                    'ninja': (3, Ninja, ('human',)),
                    
                    'max the dog': (1, MaxTheDog, ('animal', 'city')),
                    
                    'basil the dog': (1, BasilTheDog, ('animal', 'city')),
                    
                    'copy cat': (2, CopyCat, ('animal', 'city')),
                    
                    'racoon': (2, Racoon, ('animal', 'city', 'forest')),
                    
                    'fox': (2, Fox, ('animal', 'city', 'forest')),
                    
                    'cow': (2, Cow, ('animal', 'farm')),
                    
                    'shark': (1, Shark, ('animal', 'water')),
                    
                    'fish': (15, Fish, ('animal', 'water')),
                    
                    'pelican': (1, Pelican, ('animal', 'water', 'sky')),
                    
                    'lucky duck': (1, LuckyDuck, ('animal', 'water', 'sky')),
                    
                    'lady bug': (2, LadyBug, ('animal', 'sky', 'garden')),
                    
                    'mosquito': (2, Mosquito, ('animal', 'sky')),
                    
                    'snail': (1, Snail, ('animal', 'garden', 'water')),
                    
                    'dragon': (1, Dragon, ('monster', 'sky')),
                    
                    'clam': (2, Clam, ('animal', 'water')),
                    
                    'cactus': (3, Cactus, ('plant', 'desert')),
                    
                    'poison ivy': (2, PoisonIvy, ('plant', 'forest')),
                    
                    'rose': (2, Rose, ('plant', 'garden')),
                    
                    'uphalump': (1, Uphalump, ('monster',)),

                    'ghost': (2, Ghost, ('monster',)),
                    
                    'mr. squash': (1, MrSquash, ('plant', 'farm')),
                    
                    'mrs. squash': (1, MrsSquash, ('plant', 'farm')),
                    
                    'sapling': (2, Sapling, ('plant', 'forest')),
                    
                    'vines': (2, Vines, ('plant', 'garden')),
                    
                    'zombie': (2, Zombie, ('monster',)),
                    
                    'jumble': (1, Jumble, ('monster',)),
                    
                    'demon water glass': (1, DemonWaterGlass, ('monster', 'water')),
                    
                    'succosecc': (1, Succosecc, ('monster',)),
                    
                    'sunflower': (3, Sunflower, ('plant', 'garden')),
                    
                    'lemon lord': (1, LemonLord, ('plant', 'farm')),
                    
                    'wizard': (3, Wizard, ('human',)),
                    
                    'haunted oak': (1, HauntedOak, ('monster', 'plant', 'forest')),
                    
                    'office fern': (3, OfficeFern, ('plant', 'city')),
                    
                    'camel': (2, Camel, ('animal', 'desert')),
                    
                    'rattle snake': (2, RattleSnake, ('animal', 'desert')),
                    
                    'tumble weed': (3, TumbleWeed, ('plant', 'desert')),
                    
                    'mummy': (2, Mummy, ('human', 'monster', 'desert')),
                    
                    'pig': (2, Pig, ('animal', 'farm')),
                    
                    'corn': (2, Corn, ('plant', 'farm')),
                    
                    'bear': (2, Bear, ('animal', 'forest')),
                    
                    'water lilly': (2, WaterLilly, ('plant', 'water')),
                    
                    'bat': (2, Bat, ('animal', 'sky')),
                    
                    'sky flower': (2, SkyFlower, ('plant', 'sky')),
                    
                    'garden snake': (2, GardenSnake, ('animal', 'garden')),
                    
                    'big sand worm': (2, BigSandWorm, ('animal', 'desert')),
                    
                    'lost palm tree': (2, LostPalmTree, ('plant', 'desert', 'water')),
                    
                    'seaweed': (3, Seaweed, ('plant', 'water')),
                    
                    'scuba baby': (3, ScubaBaby, ('human', 'water'))
                    
                },
        
        'items': {
    
                    'fishing pole': (4, FishingPole, ('item',)),

                    'invisibility cloak': (2, InvisibilityCloak, ('equipment',)),
                    
                    'last turn pass': (4, LastTurnPass, ('item',)),
                    
                    'speed boost potion': (4, SpeedBoostPotion, ('item',)),
                    
                    'mirror': (2, Mirror, ('item',)),
                    
                    'sword': (2, Sword, ('equipment',)),
                    
                    'fertilizer': (3, Fertilizer, ('item',)),
                    
                    'treasure chest': (2, TreasureChest, ('item',)),
                    
                    'boomerang': (4, Boomerang, ('equipment',)),
                    
                    'bath tub': (2, BathTub, ('item',)),
                    
                    'detergent': (1, Detergent, ('item',)),
                    
                    'future orb': (0, FutureOrb, ('item',)),
                    
                    'knife': (4, Knife, ('item',)),
                    
                    'magic wand': (2, MagicWand, ('item',)),
                    
                    'lucky coin': (1, LuckyCoin, ('item',)),
                    
                    'sunglasses': (5, Sunglasses, ('item',)),
                    
                    'metal detector': (3, MetalDetector, ('item',)),
                    
                    'big rock': (2, BigRock, ('item',)),
                    
                    'unlucky coin': (2, UnluckyCoin, ('item',)),
                    
                    'torpedo': (2, Torpedo, ('equipment',)),
                    
                    'kite': (2, Kite, ('item',)),
                    
                    'balloon': (3, Balloon, ('item',)),
                    
                    'watering can': (2, WateringCan, ('item',)),
                    
                    'trap': (3, Trap, ('item',)),
                    
                    'flower pot': (2, FlowerPot, ('item',)),
                    
                    'bug net': (3, BugNet, ('item',))
                    
                },
                
        'treasure': {
                
                        'mustard stain': (1, MustardStain, ('treasure',)),

                        'gold': (1, Gold, ('treasure',)),
                    
                        'pearl': (4, Pearl, ('treasure',)),
                        
                        'gold coins': (10, GoldCoins, ('treasure',)),
                        
                        'bronze': (8, Bronze, ('treasure',)),
                        
                        'fools gold': (3, FoolsGold, ('treasure',)),
                        
                        'golden egg': (2, GoldenEgg, ('treasure',)),
                        
                        'magic bean': (2, MagicBean, ('treasure',))
                        
                    },
                    
        'spells': {
                
                    'spell trap': (3, SpellTrap, ('spell',)),
                    
                    'curse': (5, Curse, ('spell',)),
                    
                    'treasure curse': (2, TreasureCurse, ('spell',)),
                    
                    'item hex': (5, ItemHex, ('spell',)),
                    
                    'luck': (1, Luck, ('spell',)),
                    
                    'item leech': (4, ItemLeech, ('spell',)),
                    
                    'mummys curse': (3, MummysCurse, ('spell',)),
                    
                    'stardust': (2, Stardust, ('spell',)),
                    
                    'north wind': (1, NorthWind, ('spell',)),
                    
                    'the void': (1, TheVoid, ('spell',))

                },

        'events': {
    
                    'flu': (2, Flu, ('event',)),

                    'negative zone': (1, NegativeZone, ('event',)),
                    
                    'fishing trip': (2, FishingTrip, ('event',)),
                    
                    'item frenzy': (1, ItemFrenzy, ('event',)),
                    
                    'spell reverse': (2, SpellReverse, ('event',)),
                    
                    'sunny day': (2, SunnyDay, ('event',)),
                    
                    'parade': (2, Parade, ('event',)),
                    
                    'wind gust': (1, WindGust, ('event',)),
                    
                    #'sand storm': (2, SandStorm, ('event',)),
                    
                    'hunting season': (2, HuntingSeason, ('event',)),
                    
                    'harvest': (2, Harvest, ('event',))

                    },
                    
        'landscapes': {
    
                        'garden': (1, Garden, ('landscape',)),
                    
                        'desert': (1, Desert, ('landscape',)),
                        
                        'graveyard': (1, Graveyard, ('landscape',)),
                        
                        'city': (1, City, ('landscape',)),
                        
                        'farm': (1, Farm, ('landscape',)),
                        
                        'forest': (1, Forest, ('landscape',)),
                        
                        'water': (1, Water, ('landscape',)),
                        
                        'sky': (1, Sky, ('landscape',))
                            
                        }
                        
    }