from flask import Blueprint, request, jsonify
import random

try:
    from Agent.TriviaLC import triviaAgent
    from Agent.HangmanLC import HangMan
    trivia_agent = triviaAgent()
    hangman_agent = HangMan() # doesn't work for now
except Exception as e:
    print("Error initializing agents:", e)
    trivia_agent = None
    hangman_agent = None # doesn't work for now

start_BP = Blueprint("Start_Game", __name__)

# Game state
players = {}
player_turn_order = []
current_player = 1
game_over = False
winner = None
message = "Player 1's turn. Press the button to roll!"
message_timer = 0
message_duration = 120

# Board configuration
BOARD_SIZE = 10
snakes = {}
ladders = {}
trivia_cells = set()
hangman_cells = set()
used_positions = set()

def init_board():
    global snakes, ladders, trivia_cells, hangman_cells, used_positions
    snakes.clear()
    ladders.clear()
    used_positions.clear()
    total_cells = list(range(1, 99))

    # Create snakes
    for _ in range(5):
        while True:
            start = random.randint(4, 98)
            end = random.randint(2, start-1)
            if start not in used_positions and end not in used_positions:
                snakes[start] = end
                used_positions.add(start)
                used_positions.add(end)
                break

    # Create ladders
    for _ in range(5):
        while True:
            start = random.randint(2, 97)
            end = random.randint(start+1, 99)
            if start not in used_positions and end not in used_positions:
                ladders[start] = end
                used_positions.add(start)
                used_positions.add(end)
                break

    # Initialize minigame cells
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

"""
Roll Dice
Calculates and return the new position of each player
triggers game events
returns the contents of the mini games
"""
@start_BP.route("/roll", methods=["POST"])
def roll():
    global current_player, game_over, winner, message
    data = request.get_json()
    player_id = data.get("player_id")
    if player_id not in players:
        return jsonify({"error": "Invalid player"}), 400

    # Check if it's the player's turn
    if player_turn_order[current_player - 1] != player_id:
        return jsonify({"error": "Not your turn"}), 400

    roll_val = random.randint(1, 6)
    before_roll = players[player_id]
    pos = players[player_id] + roll_val

    print(f"Player {current_player} rolled a : {roll_val}, moving from {before_roll + 1} to {pos + 1}")
    
    # Initialize animation data
    animation_data = {
        "snake_ladder": False,
        "snake_ladder_start": None,
        "snake_ladder_end": None
    }
    
    # Check for snakes and ladders
    if (pos + 1) in ladders:
        old_pos = pos + 1
        animation_data["snake_ladder"] = True
        animation_data["snake_ladder_start"] = old_pos
        animation_data["snake_ladder_end"] = ladders[pos + 1]
        pos = ladders[pos + 1] - 1
        message = f"Player {current_player} climbed a ladder from {old_pos} to {pos + 1}!"
    elif (pos + 1) in snakes:
        old_pos = pos + 1
        animation_data["snake_ladder"] = True
        animation_data["snake_ladder_start"] = old_pos
        animation_data["snake_ladder_end"] = snakes[pos + 1]
        pos = snakes[pos + 1] - 1
        message = f"Player {current_player} was bitten by a snake and moved from {old_pos} to {pos + 1}!"
    else:
        message = f"Player {current_player} moved {roll_val} steps to position {pos+1}"
    
    # Ensure player doesn't go beyond the board
    pos = min(pos, 99)
    players[player_id] = pos

    # Check for win condition
    if pos >= 99:
        game_over = True
        winner = current_player
        message = f"Player {current_player} wins!"

    # Switch turns
    current_player = 2 if current_player == 1 else 1

    # Check for minigames
    cell = pos + 1
    mini_game = None
    content = ""

    if cell in trivia_cells and trivia_agent:
        mini_game = "trivia"
        topics = ['Sports', 'literature', 'Movies', 'Celebrities', 'Music', 'general knowledge']
        content = trivia_agent.envoke(random.choice(topics))
    elif cell in hangman_cells and hangman_agent: # doesn't work for now
        mini_game = "hangman"
        content = hangman_agent.envoke()

    return jsonify({
        "roll": roll_val,
        "before_roll": before_roll,
        "new_position": pos,
        "mini_game": mini_game,
        "content": content,
        "message": message,
        "game_over": game_over,
        "winner": winner,
        "current_player": current_player,
        **animation_data  # Include animation data in response
    })

"""
Return the board states
snakes and ladders positoins
trivia and hangman minigame positions
"""
@start_BP.route("/state", methods=["GET"])
def state():
    # Convert snake and ladder keys to strings
    snakes_str = {str(k): str(v) for k, v in snakes.items()}
    ladders_str = {str(k): str(v) for k, v in ladders.items()}
    
    return jsonify({
        "players": players,
        "snakes": snakes_str,
        "ladders": ladders_str,
        "trivia_cells": list(trivia_cells),
        "hangman_cells": list(hangman_cells),
        "current_player": current_player,
        "game_over": game_over,
        "winner": winner,
        "message": message
    })
