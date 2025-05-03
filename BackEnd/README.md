---
title: Readme
marimo-version: 0.12.2
---

# Goal

we are aiming to make this game playable on multiple devices at the same time

### What we Need for Multiplayer Hosting

We need to split your game into client and server components:

1. Client (Player UI using Pygame)
Each player runs a Pygame program that sends actions to the server and receives game state updates.

This will not be run from Flask — players run it locally.

2. Server (Flask or socket-based game logic)
The Flask app manages game state, handles player turns, updates the board, etc.


```
+------------------+          HTTP/WebSocket         +------------------+
|   Player 1 GUI   |  <-------------------------->   |     Flask Game   |
| (Pygame client)  |                                 |     Server       |
+------------------+                                 +------------------+
        |
        |                                   HTTP/WebSocket
        |                                   (same API routes)
        v
+------------------+
|   Player 2 GUI   |
| (Pygame client)  |
+------------------+
```


🖥 Server (Flask)

- Track player positions
- Roll dice
- Trigger and store mini-games per player
- Serve board state

🧑‍💻 Client (Pygame)

- Draw the board
- Send player moves
- Fetch challenges and results
- Display mini-game popup