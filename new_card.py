class Test(Card):
	def __init__(self, game, uid):
		super().__init__(game, uid, 'test', tags=[])

	def start(self, player):
		self.mode = 0
		self.players.clear()
		self.cards.clear()
		player.add_request(self, 'select')
	
	def get_selection(self, player):
		selection = []
		return selection
	
	def select(self, player, num):
		if not num:
			return
		c = player.selected.pop(0)
