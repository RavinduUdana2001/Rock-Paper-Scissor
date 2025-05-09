import random
from enum import Enum

class GameState(Enum):
    WAITING = 0
    COUNTDOWN = 1
    SHOW_GESTURES = 2
    SHOW_RESULT = 3
    GAME_OVER = 4

class Game:
    def __init__(self):
        self.choices = ["Rock", "Paper", "Scissors", "Lizard", "Spock"]
        self.rules = {
            "Rock": ["Scissors", "Lizard"],
            "Paper": ["Rock", "Spock"],
            "Scissors": ["Paper", "Lizard"],
            "Lizard": ["Spock", "Paper"],
            "Spock": ["Scissors", "Rock"]
        }
        self.reset_game()

    def reset_game(self):
        self.user_score = 0
        self.computer_score = 0
        self.round = 0
        self.max_rounds = 5
        self.state = GameState.WAITING
        self.countdown_value = 3
        self.computer_choice = None
        self.user_choice = None
        self.result = None

    def start_new_round(self):
        if self.round < self.max_rounds:
            self.state = GameState.COUNTDOWN
            self.countdown_value = 3
            self.computer_choice = None
            self.user_choice = None
            self.result = None
            return True
        else:
            self.state = GameState.GAME_OVER
            return False

    def update_countdown(self):
        if self.countdown_value > 0:
            self.countdown_value -= 1
            return str(self.countdown_value + 1)
        else:
            self.state = GameState.SHOW_GESTURES
            self.computer_choice = random.choice(self.choices)
            return "Shoot!"

    def set_user_choice(self, gesture):
        if self.state == GameState.SHOW_GESTURES and gesture != "Unknown":
            self.user_choice = gesture
            self.determine_result()
            self.round += 1
            self.state = GameState.SHOW_RESULT

    def determine_result(self):
        if self.user_choice == self.computer_choice:
            self.result = "Tie!"
        elif self.computer_choice in self.rules[self.user_choice]:
            self.result = "You win!"
            self.user_score += 1
        else:
            self.result = "Computer wins!"
            self.computer_score += 1

    def is_game_over(self):
        return self.round >= self.max_rounds

    def start_new_game(self):
        self.reset_game()
