from Agent.agent import agent
class triviaAgent(agent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    def envoke(self, topic):
        response = self.chain().invoke({"question": f"Generate a multiple-choice trivia question about {topic}."})
        return response
    def check_answer(self, answer):
        check_answer = self.chain().invoke({"question": f"""Is this the correct answer, {answer}, True or False"""})
        return check_answer
    