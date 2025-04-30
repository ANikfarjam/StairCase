from flask import Blueprint, request, jsonify
import random

try:
    from Agent.TriviaLC import triviaAgent
    from Agent.HangmanLC import HangMan
    trivia_agent = triviaAgent()
    hangman_agent = HangMan()
except Exception as e:
    print("Error initializing agents:", e)
    trivia_agent = None
    hangman_agent = None

start_BP = Blueprint("Start_Game", __name__)

players = {}
player_turn_order = []
snakes = {}
ladders = {}
trivia_cells = set()
hangman_cells = set()
BOARD_SIZE = 100

def init_board():
    global snakes, ladders, trivia_cells, hangman_cells
    snakes.clear()
    ladders.clear()
    total_cells = list(range(1, 99))

    for _ in range(5):
        start = random.randint(20, 98)
        end = random.randint(1, start - 1)
        snakes[end] = start
    for _ in range(5):
        start = random.randint(1, 80)
        end = random.randint(start + 1, 99)
        ladders[start] = end

    random.shuffle(total_cells)
    trivia_cells.update(total_cells[:15])
    hangman_cells.update(total_cells[15:30])

init_board()

@start_BP.route("/join", methods=["POST"])
def join():
    try:
        player_id = f"player_{len(players)+1}"
        players[player_id] = 0
        player_turn_order.append(player_id)
        print(f"✅ /join called → {player_id}")
        return jsonify({"player_id": player_id})
    except Exception as e:
        print("❌ ERROR in /join:", str(e))
        return jsonify({"error": "Server failed"}), 500


@start_BP.route("/roll", methods=["POST"])
def roll():
    data = request.get_json()
    player_id = data.get("player_id")
    if player_id not in players:
        return jsonify({"error": "Invalid player"}), 400

    roll_val = random.randint(1, 6)
    pos = players[player_id] + roll_val
    pos = ladders.get(pos, pos)
    pos = snakes.get(pos, pos)
    pos = min(pos, 99)
    players[player_id] = pos

    cell = pos + 1
    mini_game = None
    content = ""

    if cell in trivia_cells and trivia_agent:
        mini_game = "trivia"
        topics = ['Sports', 'literature', 'Movies', 'Celebrities', 'Music', 'general knowledge']
        content = trivia_agent.envoke(random.choice(topics))
    elif cell in hangman_cells and hangman_agent:
        mini_game = "hangman"
        content = hangman_agent.envoke()

    return jsonify({
        "roll": roll_val,
        "new_position": pos,
        "mini_game": mini_game,
        "content": content
    })

@start_BP.route("/state", methods=["GET"])
def state():
    return jsonify({
        "players": players,
        "snakes": snakes,
        "ladders": ladders,
        "trivia_cells": list(trivia_cells),
        "hangman_cells": list(hangman_cells)
    })
