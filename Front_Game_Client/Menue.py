import pygame
import requests
import sys
import os
import time
import atexit
import signal
import Front_Game_Client.game_client
pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 900, 750
FONT = pygame.font.SysFont("Arial", 22)
# SERVER = "http://127.0.0.1:5000"
SERVER="http://10.0.0.120:5001"
WHITE = (255, 255, 255)
GRAY = (240, 240, 240)
BLUE = (80, 120, 255)
BLACK = (0, 0, 0)
BUTTON_COLOR = (30, 144, 255)
RED = (200, 50, 50)
GREEN = (50, 200, 100)
ORANGE = (255, 140, 0)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Staircase Game Menu")

user_id = ""
user_info = {}
friends = []
friend_requests = []
search_result = None
search_text = ""
message = ""
party_members = []
pending_invite_from = None

# Load logo
logo = None
try:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    logo_path = os.path.join(base_dir, "../BackEnd/logo.png")
    if os.path.exists(logo_path):
        logo = pygame.image.load(logo_path)
        logo = pygame.transform.scale(logo, (150, 150))
except:
    pass

def update_status(is_online=True):
    try:
        requests.post(f"{SERVER}/set_status", json={
            "username": user_id,
            "status": is_online
        })
    except:
        pass

atexit.register(lambda: update_status(False))
signal.signal(signal.SIGINT, lambda sig, frame: sys.exit(0))
signal.signal(signal.SIGTERM, lambda sig, frame: sys.exit(0))

def start_game():
    try:
        res = requests.post(f"{SERVER}/join")
        if res.status_code == 200:
            player_id = res.json()["player_id"]
            print("Joined game as:", player_id)
            # Now launch the game loop or load game scene
            # You can import and call a game function here
            import game_client
            game_client.main(player_id)
        else:
            print("Failed to join game.")
    except Exception as e:
        print("Error starting game:", str(e))

def send_game_invite(friend_username):
    try:
        res = requests.post(f"{SERVER}/send_invite", json={
            "from": user_info["Username"],
            "to": friend_username
        })
        return res.status_code == 200
    except:
        return False

def fetch_party():
    global party_members
    try:
        res = requests.get(f"{SERVER}/get_party", params={"username": user_info["Username"]})
        if res.status_code == 200:
            party_members = res.json().get("party", [])
    except:
        party_members = []

def check_for_invite():
    global pending_invite_from
    try:
        res = requests.get(f"{SERVER}/check_invite", params={"username": user_info["Username"]})
        if res.status_code == 200:
            from_user = res.json().get("from")
            if from_user:
                pending_invite_from = from_user
    except:
        pass

def draw_text(text, x, y, color=BLACK):
    rendered = FONT.render(text, True, color)
    screen.blit(rendered, (x, y))

def draw_button(text, x, y, w, h, color=BUTTON_COLOR):
    pygame.draw.rect(screen, color, (x, y, w, h), border_radius=8)
    txt = FONT.render(text, True, WHITE)
    screen.blit(txt, (x + 10, y + 10))
    return pygame.Rect(x, y, w, h)

def fetch_user_info():
    global user_info
    try:
        res = requests.get(f"{SERVER}/get_use_info", params={"user_id": user_id})
        user_info.update(res.json())
        if "Username" not in user_info:
            user_info["Username"] = user_id
    except:
        user_info = {"Points": 0, "NumberOfWins": 0, "Username": user_id}

def fetch_friend_data():
    global friends, friend_requests
    try:
        res = requests.get(f"{SERVER}/get_friends_list", params={"user_id": user_info["Username"]})
        friends = res.json().get("friends", [])

        req = requests.get(f"{SERVER}/get_friend_requests", params={"user_id": user_info["Username"]})
        received_ids = req.json().get("received", [])

        friend_requests = []
        for uid in received_ids:
            user_doc = requests.get(f"{SERVER}/get_username_by_id", params={"doc_id": uid})
            if user_doc.status_code == 200:
                data = user_doc.json()
                friend_requests.append({
                    "id": uid,
                    "Username": data.get("Username", uid)
                })
    except:
        friends = []
        friend_requests = []

def search_user_by_username(username):
    try:
        res = requests.get(f"{SERVER}/search_user_by_username", params={"username": username})
        if res.status_code == 200:
            return res.json()["user"]
    except:
        pass
    return None

def send_friend_request(receiver_username):
    try:
        res = requests.post(f"{SERVER}/send_friend_request", json={
            "sender_username": user_info.get("Username"),
            "receiver_username": receiver_username
        })
        return res.status_code == 200
    except:
        return False

def accept_friend(sender_id):
    try:
        me = requests.get(f"{SERVER}/search_user_by_username", params={"username": user_info["Username"]})
        if me.status_code == 200:
            user_doc = me.json()
            user_doc_id = user_doc["user"]["id"]
            requests.post(f"{SERVER}/accept_friend_request", json={
                "user_id": user_doc_id,
                "sender_id": sender_id
            })
    except:
        pass

def reject_friend(sender_id):
    try:
        me = requests.get(f"{SERVER}/search_user_by_username", params={"username": user_info["Username"]})
        if me.status_code == 200:
            user_doc = me.json()
            user_doc_id = user_doc["user"]["id"]
            requests.post(f"{SERVER}/reject_friend_request", json={
                "user_id": user_doc_id,
                "sender_id": sender_id
            })
    except:
        pass

def login_screen():
    global user_id
    input_box_id = pygame.Rect(320, 230, 240, 40)
    input_box_pw = pygame.Rect(320, 300, 240, 40)
    active_box = None
    id_text, pw_text = '', ''
    show_error = False

    while True:
        screen.fill(WHITE)
        if logo:
            screen.blit(logo, (SCREEN_WIDTH // 2 - logo.get_width() // 2, 40))
        draw_text("User ID (Username):", 320, 200)
        draw_text("Password:", 320, 270)
        pygame.draw.rect(screen, GRAY if active_box != 'id' else BLUE, input_box_id, 2)
        screen.blit(FONT.render(id_text, True, BLACK), (input_box_id.x+5, input_box_id.y+5))
        pygame.draw.rect(screen, GRAY if active_box != 'pw' else BLUE, input_box_pw, 2)
        screen.blit(FONT.render('*' * len(pw_text), True, BLACK), (input_box_pw.x+5, input_box_pw.y+5))
        draw_text("Press Enter when ready", 340, 360, ORANGE)

        if show_error:
            draw_text("Missing credentials!", 340, 390, RED)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                update_status(False)
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                active_box = 'id' if input_box_id.collidepoint(event.pos) else 'pw' if input_box_pw.collidepoint(event.pos) else None
            if event.type == pygame.KEYDOWN and active_box:
                if event.key == pygame.K_RETURN:
                    if id_text and pw_text:
                        user_id = id_text.strip()
                        fetch_user_info()
                        update_status(True)
                        fetch_friend_data()
                        fetch_party()
                        return
                    else:
                        show_error = True
                elif event.key == pygame.K_BACKSPACE:
                    if active_box == 'id': id_text = id_text[:-1]
                    elif active_box == 'pw': pw_text = pw_text[:-1]
                else:
                    if active_box == 'id': id_text += event.unicode
                    elif active_box == 'pw': pw_text += event.unicode
        pygame.display.update()
        pygame.time.delay(50)
def menu_screen():
    global search_text, search_result, message, pending_invite_from
    clock = pygame.time.Clock()
    input_box = pygame.Rect(500, 440, 220, 35)
    active = False
    last_refresh = 0
    last_check = 0

    while True:
        screen.fill((250, 250, 255))
        draw_text(f"User: {user_info.get('Username', user_id)}", 20, 20)
        draw_text(f"Wins: {user_info.get('NumberOfWins', 0)}", 20, 60)
        draw_text(f"Points: {user_info.get('Points', 0)}", 20, 100)

        if time.time() - last_refresh > 5:
            fetch_friend_data()
            fetch_party()
            check_for_invite()
            last_refresh = time.time()

        #  Auto-start check
        # if time.time() - last_check > 3:
        #     try:
        #         res = requests.get(f"{SERVER}/get_party_status", params={"username": user_info["Username"]})
        #         if res.status_code == 200 and res.json().get("game_started"):
        #             print("Game started remotely. Launching...")
        #             import importlib.util
        #             import sys
        #             game_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "game_client.py"))
        #             spec = importlib.util.spec_from_file_location("game_client", game_path)
        #             game_module = importlib.util.module_from_spec(spec)
        #             sys.modules["game_client"] = game_module
        #             spec.loader.exec_module(game_module)
        #             game_module.main()
        #     except Exception as e:
        #         print("Auto-start error:", e)
        #     last_check = time.time()

        # Friends List
        draw_text("Friends:", 40, 140)
        for i, f in enumerate(friends[:5]):
            y = 170 + i * 50
            pygame.draw.rect(screen, (220, 235, 255), (40, y, 360, 40), border_radius=10)
            draw_text(f['Username'], 80, y + 10)
            dot_color = GREEN if f.get("Online") else RED
            pygame.draw.circle(screen, dot_color, (55, y + 20), 8)
            if f.get("Online"):
                invite_btn = draw_button("Invite", 260, y + 5, 80, 28, ORANGE)
                if pygame.mouse.get_pressed()[0]:
                    if invite_btn.collidepoint(pygame.mouse.get_pos()):
                        if send_game_invite(f["Username"]):
                            message = f"Invited {f['Username']}!"
                        else:
                            message = f"Failed to invite {f['Username']}"

        # Party List
        draw_text("Party:", 40, 460)
        reset_btn = draw_button("Reset", 300, 460, 80, 30, RED)
        pygame.draw.rect(screen, (245, 255, 245), pygame.Rect(40, 490, 360, 100), border_radius=12)
        for i, member in enumerate(party_members):
            draw_text(f"- {member}", 60, 500 + i * 20, BLACK)

        # Friend Requests
        draw_text("Requests:", 500, 140)
        for i, sender in enumerate(friend_requests[:5]):
            y = 170 + i * 60
            pygame.draw.rect(screen, (255, 240, 240), (500, y, 360, 50), border_radius=10)
            draw_text(sender["Username"], 520, y + 15)

            acc_btn = draw_button("Accept", 700, y + 10, 70, 30, GREEN)
            rej_btn = draw_button("Reject", 770, y + 10, 70, 30, RED)

            if pygame.mouse.get_pressed()[0]:
                mouse_pos = pygame.mouse.get_pos()
                if acc_btn.collidepoint(mouse_pos):
                    accept_friend(sender["id"])
                    fetch_friend_data()
                elif rej_btn.collidepoint(mouse_pos):
                    reject_friend(sender["id"])
                    fetch_friend_data()

        # Search Box
        pygame.draw.rect(screen, GRAY if not active else BLUE, input_box, 2)
        screen.blit(FONT.render(search_text, True, BLACK), (input_box.x + 5, input_box.y + 5))
        draw_text("Search by Username:", 500, 410)
        search_btn = draw_button("Search", 730, 440, 100, 35)

        if search_result == "not_found":
            draw_text("User not found.", 500, 500, RED)
        elif search_result == "already_friends":
            draw_text("Already your friend or request sent.", 500, 500, ORANGE)
        elif search_result and isinstance(search_result, dict):
            draw_text(f"Found: {search_result['Username']}", 500, 500)
            req_btn = draw_button("Send Request", 650, 495, 150, 35)
            if pygame.mouse.get_pressed()[0]:
                if req_btn.collidepoint(pygame.mouse.get_pos()):
                    if send_friend_request(search_result["Username"]):
                        message = "Friend request sent."
                        search_result = None
                        fetch_friend_data()
                    else:
                        message = "Failed to send request."
        if message:
            draw_text(message, 500, 530, GREEN)

        # Start Game Button
        start_btn = draw_button("Start Game", 350, 610, 200, 45)
        if pygame.mouse.get_pressed()[0] and start_btn.collidepoint(pygame.mouse.get_pos()):
            try:
                party_res = requests.get(f"{SERVER}/get_party", params={"username": user_info["Username"]})
                party = party_res.json().get("party", [])

                if user_info["Username"] not in party:
                    party.append(user_info["Username"])

                player_ids = []
                for member in party:
                    join_res = requests.post(f"{SERVER}/join", json={"username": member})
                    if join_res.status_code == 200:
                        player_id = join_res.json().get("player_id")
                        player_ids.append((member, player_id))
                    else:
                        print(f"Failed to join for {member}")

                # Broadcast game start
                for member in party:
                    requests.post(f"{SERVER}/start_game_signal", json={"username": member})

                print("Players joined:", player_ids)
                import importlib.util
                import sys
                game_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "game_client.py"))
                spec = importlib.util.spec_from_file_location("game_client", game_path)
                game_module = importlib.util.module_from_spec(spec)
                sys.modules["game_client"] = game_module
                spec.loader.exec_module(game_module)
                game_module.main()
            except Exception as e:
                print("Failed to start game:", e)

        # Modal Invite Popup
        if pending_invite_from:
            modal = pygame.Rect(200, 200, 500, 200)
            pygame.draw.rect(screen, (255, 255, 240), modal, border_radius=12)
            pygame.draw.rect(screen, BLACK, modal, 2, border_radius=12)
            draw_text(f"{pending_invite_from} invited you!", 250, 240, BLACK)
            accept_btn = draw_button("Accept", 250, 300, 100, 40, GREEN)
            decline_btn = draw_button("Decline", 480, 300, 100, 40, RED)

            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                if accept_btn.collidepoint(pos):
                    requests.post(f"{SERVER}/accept_invite", json={"from": pending_invite_from, "to": user_info["Username"]})
                    pending_invite_from = None
                    fetch_party()
                elif decline_btn.collidepoint(pos):
                    requests.post(f"{SERVER}/decline_invite", json={"from": pending_invite_from, "to": user_info["Username"]})
                    pending_invite_from = None

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                update_status(False)
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos): active = True
                else: active = False
                if search_btn.collidepoint(event.pos):
                    result = search_user_by_username(search_text)
                    if not result:
                        search_result = "not_found"
                    elif result["Username"] == user_info["Username"] or result["Username"] in [f["Username"] for f in friends]:
                        search_result = "already_friends"
                    else:
                        search_result = result
                    message = ""
                if reset_btn.collidepoint(event.pos):
                    try:
                        requests.post(f"{SERVER}/reset_party", json={"username": user_info["Username"]})
                        fetch_party()
                        message = "Party reset!"
                    except:
                        message = "Failed to reset party."
            if event.type == pygame.KEYDOWN and active:
                if event.key == pygame.K_BACKSPACE:
                    search_text = search_text[:-1]
                elif event.key == pygame.K_RETURN:
                    result = search_user_by_username(search_text)
                    search_result = result if result else "not_found"
                else:
                    search_text += event.unicode

        pygame.display.update()
        clock.tick(60)



if __name__ == "__main__":
    login_screen()
    menu_screen()
