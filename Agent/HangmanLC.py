from Agent.agent import agent
class HangMan(agent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    def envoke(self):
        response = self.chain().invoke({"question": "Generate a randome word for a hangman game. Only give me one word response!"})
        return response