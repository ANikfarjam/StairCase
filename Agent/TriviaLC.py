from Agent.agent import agent
from BackEnd.app import app
class triviaAgent(agent):
    """
    This is the Langchain agent for generating trivia questions and checking answers

    Returns:
        def envoke(self,topic):
            This function returns the trivia question and the 4 choices
        def check_answer(self,answer):
            Returns a True or False based on whether the player's answer is correct
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_question = None
        self.current_choices = None
        
    def envoke(self, topic):
        response = self.chain().invoke({"question": f"Generate a multiple-choice trivia question under 75 characters about {topic}. Only return the question and the 4 choices."})
        self.current_question = response
        app.logger.info(self.current_question)
        # Extract choices from response
        lines = response.split('\n')
        app.logger.info(lines)
        self.current_choices = [line.strip() for line in lines if line.strip().startswith(('A)', 'B)', 'C)', 'D)'))]
        app.logger.info(self.current_choices)
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