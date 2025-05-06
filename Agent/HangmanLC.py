from Agent.agent import agent
import random

class HangMan(agent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_word = None
        self.revealed = None
        self.lives = 3
        
    def envoke(self):
        response = self.chain().invoke({"question": "Generate a random word for a hangman game. Only give me one word response!"})
        self.current_word = response.strip().upper()
        # Initialize revealed letters with 2 random letters shown
        self.revealed = list("_" * len(self.current_word))
        indices = random.sample(range(len(self.current_word)), 2)
        for i in indices:
            self.revealed[i] = self.current_word[i]
        self.revealed = "".join(self.revealed)
        return self.revealed
        
    def check_answer(self, answer):
        if not self.current_word:
            return False
            
        answer = answer.strip().upper()
        if answer == self.current_word:
            return True
            
        # Wrong guess - lose a life and reveal a letter
        self.lives -= 1
        if self.lives > 0:
            # Reveal one more letter
            word_list = list(self.revealed)
            hidden_indices = [i for i, c in enumerate(word_list) if c == "_"]
            if hidden_indices:
                reveal_index = random.choice(hidden_indices)
                word_list[reveal_index] = self.current_word[reveal_index]
                self.revealed = "".join(word_list)
        return False
        
    def get_game_state(self):
        return {
            "revealed": self.revealed,
            "lives": self.lives,
            "message": f"Wrong guess! {self.lives} lives remaining." if self.lives > 0 else "Out of lives!"
        }
        
    def reset(self):
        self.current_word = None
        self.revealed = None
        self.lives = 3