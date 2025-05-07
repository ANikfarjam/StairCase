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

# Game state
players = {}
player_turn_order = []
current_player = 1
game_over = False
winner = None
message = "Player 1's turn. Press the button to roll!"
message_timer = 0
message_duration = 120

# Hangman game state
hangman_words = {}
hangman_revealed = {}
hangman_lives = {}

# Board configuration
BOARD_SIZE = 10
snakes = {}
ladders = {}
trivia_cells = set()
hangman_cells = set()
used_positions = set()
total_cells = list(range(2, 88))

def init_board():
    """ 
    Initializes the board with obstacles: snakes, ladders, trivia, and hangman minigames.

    Parameters: None

    Returns: None
    """
    global snakes, ladders, trivia_cells, hangman_cells, used_positions
    snakes.clear()
    ladders.clear()
    used_positions.clear()
    trivia_cells.clear()
    hangman_cells.clear()

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
    trivia_cells.update(total_cells[:10])
    hangman_cells.update(total_cells[10:20])

init_board()

# @start_BP.route("/join", methods=["POST"])
# def join():
#     try:
#         player_id = f"player_{len(players)+1}"
#         players[player_id] = 0
#         player_turn_order.append(player_id)
#         print(f"/join called → {player_id}")
#         return jsonify({"player_id": player_id})
#     except Exception as e:
#         print("ERROR in /join:", str(e))
#         return jsonify({"error": "Server failed"}), 500

# @start_BP.route("/join", methods=["POST"])
# def join():
#     try:
#         player_id = f"player_{len(players)+1}"
#         players[player_id] = 0
#         player_turn_order.append(player_id)
#         print(f"✅ /join called → {player_id}")
#         return jsonify({"player_id": player_id})
#     except Exception as e:
#         print("❌ ERROR in /join:", str(e))
#         return jsonify({"error": "Server failed"}), 500

@start_BP.route("/join", methods=["POST"])
def join():
    """ 
    Handles joining the game for 2 player support

    Parameters: None

    Returns: A json object with the player_id
    """
    try:
        data = request.get_json()
        username = data.get("username", f"user_{len(players)+1}")
        
        player_id = f"player_{len(players)+1}"
        players[player_id] = 0
        player_turn_order.append(player_id)

        print(f"✅ /join called → {player_id} for {username}")
        print(f"Current players: {players}")
        
        return jsonify({"player_id": player_id})
    except Exception as e:
        print("❌ ERROR in /join:", str(e))
        return jsonify({"error": "Server failed"}), 500

@start_BP.route("/roll", methods=["POST"])
def roll():
    """
    Handles the rolling dice logic:
    Calculates and return the new position of each player,
    triggers game events of moving down a snake or moving up a ladder,
    and returns the contents of the mini games.

    Parameters: None
    
    Returns: A JSON dictionaryresponse containing:
            - roll: The dice roll value (1-6)
            - before_roll: Player's position before the roll
            - new_position: Player's position after the roll
            - mini_game: Type of minigame if landed on one ('trivia' or 'hangman')
            - content: Prompt from minigame when landed on
            - message: Game message to display
            - game_over: Boolean indicating if game is over
            - winner: Player number that won the game
            - current_player: Current player's turn
            - animation_data: positions of initial and ending positions of snakes and ladders for animation movement
                - snake_ladder: Boolean indicating if landed on snake/ladder
                - snake_ladder_start: Starting position of snake/ladder
                - snake_ladder_end: Ending position of snake/ladder
    """
    global current_player, game_over, winner, message
    data = request.get_json()
    player_id = data.get("player_id")
    if player_id not in players:
        return jsonify({"error": "Invalid player"}), 400

    if current_player - 1 >= len(player_turn_order):
        return jsonify({"error": "Not enough players joined"}), 400

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
        # topics = ['Sports', 'literature', 'Movies', 'Celebrities', 'Music', 'general knowledge']
        topics = ['Science', 'Geography', 'Math', 'History', 'Pop Culture', 'general knowledge', 'Animals', 'Food', 'Technology', 'Literature', 'Art', 'Sports']

        content = trivia_agent.envoke(random.choice(topics))
    elif cell in hangman_cells and hangman_agent:
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

@start_BP.route("/state", methods=["GET"])
def state():
    """
    Returns the board states, including snake and ladder positions,
    trivia and hangman cell positions, the current player's turn,
    whether the game is over, the winner, and the current message.

    Parameters: None

    Returns: A JSON dictionary response containing:
        - players: Player positions
        - snakes: Snake positions
        - ladders: Ladder positions
        - trivia_cells: Trivia cell positions
        - hangman_cells: Hangman cell positions
        - current_player: Current player's turn
        - game_over: Boolean indicating if game is over
        - winner: Player number that won the game
        - message: Current game message
    """
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

@start_BP.route("/submit_answer", methods=["POST"])
def submit_answer():
    """
    Handles the submission of user answers to the trivia and hangman minigames.

    Parameters: None

    Returns: 
        If its for a trivia question: 
            correct: Boolean indicating if the answer is correct
            message: Game message to display
            new_position: Player's position after the minigame
            game_type: Type of minigame ('trivia' or 'hangman')
        If its for a hangman question:
            correct: Boolean indicating if the answer is correct
            revealed: Partially hidden word for hangman
            lives: Number of guesses remaining for hangman
            new_position: Player's position after the minigame
            message: Game message to display
            game_type: Type of minigame ('trivia' or 'hangman')
    """
    global game_over, winner, message
    try:
        data = request.get_json()
        player_id = data.get("player_id")
        answer = data.get("answer")
        
        print(f"Received answer submission - Player: {player_id}, Answer: {answer}")
        
        if not player_id or not answer:
            print("Missing player_id or answer")
            return jsonify({"error": "Missing player_id or answer"}), 400
            
        if player_id not in players:
            print(f"Invalid player_id: {player_id}")
            return jsonify({"error": "Invalid player"}), 400
            
        # Check if it's a trivia question
        if not trivia_agent and not hangman_agent:
            print("No game agents available")
            return jsonify({"error": "No game agents available"}), 500
            
        try:
            current_pos = players[player_id]
            player_answered = current_player
            if player_answered == 1:
                player_answered = 2
            else:
                player_answered = 1

            # Handle trivia answer
            if trivia_agent and current_pos + 1 in trivia_cells:
                is_correct = trivia_agent.check_answer(answer)
                if is_correct:
                    new_pos = min(current_pos + 10, 98)
                    message = f"Correct answer! Player {player_answered} moves forward to position {new_pos + 1}!"
                else:
                    new_pos = max(current_pos - 10, 0)
                    message = f"Incorrect answer! Player {player_answered} moves back to position {new_pos + 1}!"
                players[player_id] = new_pos
                return jsonify({
                    "correct": is_correct,
                    "message": message,
                    "new_position": new_pos,
                    "game_type": "trivia"
                })
            
            # Handle hangman answer
            elif hangman_agent and current_pos + 1 in hangman_cells:
                if not hangman_agent.current_word:
                    # Initialize hangman game
                    revealed = hangman_agent.envoke()
                    return jsonify({
                        "game_type": "hangman",
                        "revealed": revealed,
                        "lives": hangman_agent.lives,
                        "message": "Guess the word!"
                    })
                
                # Check hangman answer
                is_correct = hangman_agent.check_answer(answer)
                
                if is_correct:
                    new_pos = min(current_pos + 10, 98)
                    message = f"Correct! Player {player_answered} moves forward to position {new_pos + 1}!"
                    players[player_id] = new_pos
                    hangman_agent.reset()
                    return jsonify({
                        "correct": True,
                        "message": message,
                        "new_position": new_pos,
                        "game_type": "hangman"
                    })
                else:
                    game_state = hangman_agent.get_game_state()
                    if hangman_agent.lives <= 0:
                        new_pos = max(current_pos - 10, 0)
                        message = f"Out of lives! Player {player_answered} moves back to position {new_pos + 1}!"
                        players[player_id] = new_pos
                        hangman_agent.reset()
                        return jsonify({
                            "correct": False,
                            "message": message,
                            "new_position": new_pos,
                            "game_type": "hangman"
                        })
                    else:
                        return jsonify({
                            "correct": False,
                            "revealed": game_state["revealed"],
                            "lives": game_state["lives"],
                            "message": game_state["message"],
                            "game_type": "hangman"
                        })
            
            return jsonify({"error": "Not in a minigame cell"}), 400
            
        except Exception as e:
            print(f"Error checking answer: {str(e)}")
            return jsonify({"error": f"Error checking answer: {str(e)}"}), 500
            
    except Exception as e:
        print(f"❌ ERROR in /submit_answer: {str(e)}")
        return jsonify({"error": f"Server failed: {str(e)}"}), 500

@start_BP.route('/restart', methods=['POST'])
def restart_game():
    global players, player_turn_order, current_player, game_over, winner, message, message_timer

    # ✅ Clear all player data so join starts fresh
    players.clear()
    player_turn_order.clear()

    current_player = 1
    game_over = False
    winner = None
    message = "Player 1's turn. Press the button to roll!"
    message_timer = 0

    init_board()

    return jsonify({"status": "success"})

@start_BP.route('/new_game', methods=['POST'])
def new_game():
    """
    Restarts the game so that the players can play again

    Parameters: None

    Returns: None
    """
    global player1_pos, player2_pos, current_player, game_over, winner, message, message_timer, animating, current_anim_pos, target_anim_pos, trivia_cells, hangman_cells

    for pid, pos in players.items():
        players[pid] = 0

    current_player = 1
    game_over = False
    winner = None
    message = ""
    message_timer = 0
    animating = False
    current_anim_pos = [0, 0]
    target_anim_pos = [0, 0]

    init_board()