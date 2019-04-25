class PictionaryGame:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.secret = None
        self.reward = 0
        self.running = False

    def start_game(self):
        self.running = True

    def end_game(self):
        self.running = False

    def set_prize_reward(self, amount):
        self.reward = int(amount)

    def set_secret_word(self, secret):
        self.secret = secret

    def get_secret_word(self):
        if self.secret is not None:
            return self.secret

    def game_service(self, user, message):
        if not self.running:
            return False
        word_list = message.split(' ')
        word_list = [x.strip() for x in word_list]
        for x in word_list:
            if x.lower() == self.secret.lower():
                self.end_game()
                self.db_manager.change_user_points(str(user), self.reward)
                output = "User: " + str(user) + " has won! " + str(self.reward) + " points were added.\n"
                return output
        return False
