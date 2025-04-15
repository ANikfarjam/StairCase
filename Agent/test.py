from TriviaLC import triviaAgent
from HangmanLC import HangMan

trivia_agent = triviaAgent()
question = trivia_agent.envoke(topic="movies")
print(question)
answer = input('Please Enter your answer')
print(trivia_agent.check_answer(answer=answer))