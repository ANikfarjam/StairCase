from Agent.agent import agent
class triviaAgent(agent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_question = None
        self.current_choices = None
        
    def envoke(self, topic):
        response = self.chain().invoke({"question": f"Generate a multiple-choice trivia question under 75 characters about {topic}. Only return the question and the 4 choices."})
        self.current_question = response
        # Extract choices from response
        lines = response.split('\n')
        self.current_choices = [line.strip() for line in lines if line.strip().startswith(('A)', 'B)', 'C)', 'D)'))]
        return response
        
    def check_answer(self, answer):
        if not self.current_question or not self.current_choices:
            return False
            
        # Check if the answer matches any of the choices
        answer = answer.strip().upper()
        for choice in self.current_choices:
            if choice.startswith(answer):
                # Ask the LLM to verify if this is the correct answer
                check = self.chain().invoke({
                    "question": f"Given this trivia question and its choices:\n{self.current_question}\n\nIs '{choice}' the correct answer? Answer only with True or False."
                })
                return "True" in check
        return False