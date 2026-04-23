import asyncio  
import base64
import hashlib
import os
import re
import random
import pymysql
from pymysql import IntegrityError, MySQLError

from game import Game, Player
from rankedqueue import RankedQueue

# DB Config can be changed depending on what we need going off db.md
DB_CONFIG = {
    "host": os.getenv("POLARIS_DB_HOST", "127.0.0.1"),
    "port": int(os.getenv("POLARIS_DB_PORT", "3306")),
    "user": os.getenv("POLARIS_DB_USER", "root"),
    "password": os.getenv("POLARIS_DB_PASSWORD", "polaris"),
    "database": os.getenv("POLARIS_DB_NAME", "chinese_checkers"),
    "cursorclass": pymysql.cursors.DictCursor,
    "autocommit": False,
}

USERNAME_RE = re.compile(r"^[A-Za-z0-9_]{3,30}$")
PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 128
PBKDF2_ITERATIONS = 200_000

games: dict[int, dict] = {}  # game_id -> {"game": Game, "code": str | None}
game_codes: dict[str, int] = {}  # game_code -> game_id (for private lobbies)
ranked_queue = RankedQueue()

# CLIENT MESSAGES
# event is a dictionary (loaded JSON object) directly from client

def _get_connection():
    return pymysql.connect(**DB_CONFIG)

def _hash_password(password, salt=None):
    if salt is None:
        salt = os.urandom(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PBKDF2_ITERATIONS,
    )
    
    return (
        base64.b64encode(password_hash).decode("ascii"),
        base64.b64encode(salt).decode("ascii"),
    )
    
def signup(event):
    username = event.get("name")
    password = event.get("pass")

    if not isinstance(username, str):
        return {"code": 4}

    username = username.strip()
    if not USERNAME_RE.fullmatch(username):
        return {"code": 4}

    if not isinstance(password, str):
        return {"code": 4}

    if not (PASSWORD_MIN_LENGTH <= len(password) <= PASSWORD_MAX_LENGTH):
        return {"code": 4}

    password_hash, salt = _hash_password(password)

    try:
        connection = _get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT id FROM users WHERE name = %s", (username,))
                if cursor.fetchone() is not None:
                    return {"code": 5}

                cursor.execute(
                    """
                    INSERT INTO users (name, password_hash, salt)
                    VALUES (%s, %s, %s)
                    """,
                    (username, password_hash, salt),
                )

            connection.commit()
            return {"code": 0}
        finally:
            connection.close()
    except IntegrityError:
        return {"code": 5}
    except MySQLError:
        return {"code": -1}


def login(event):
    username = event.get("name")
    password = event.get("pass")

    if not isinstance(username, str):
        return {"code": 4}

    username = username.strip()
    if not USERNAME_RE.fullmatch(username):
        return {"code": 4}

    if not isinstance(password, str):
        return {"code": 4}

    if not (PASSWORD_MIN_LENGTH <= len(password) <= PASSWORD_MAX_LENGTH):
        return {"code": 4}

    try:
        connection = _get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT password_hash, salt FROM users WHERE name = %s",
                    (username,),
                )
                user = cursor.fetchone()
                if user is None:
                    return {"code": 4}

                stored_hash = user["password_hash"]
                salt = base64.b64decode(user["salt"])

                computed_hash, _ = _hash_password(password, salt)
                if computed_hash == stored_hash:
                    return {"code": 0}
                else:
                    return {"code": 4}
        finally:
            connection.close()
    except MySQLError:
        return {"code": -1}


async def game_request(event):
    username = event.get("name")
    
    if not isinstance(username, str) or not username.strip():
        return {"code": 4}
    
    username = username.strip()
    
    try:
        connection = _get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT score FROM users WHERE name = %s",
                    (username,),
                )
                user = cursor.fetchone()
                if user is None:
                    return {"code": 4}
                
                user_elo = user["score"]
        finally:
            connection.close()
    except MySQLError:
        return {"code": -1}
    
    # Add to queue
    await ranked_queue.add_player(username, user_elo)
    
    # Try to find immediate match
    matched = await ranked_queue.try_match()
    if matched:
        # Create game with matched players
        game_id = create_ranked_game(matched)
        return {"code": 0, "status": "matched", "game_id": game_id} # TODO Not correct currently, need to ask about how to send it to frontend
    else:
        return {"code": 0, "status": "queued"} # TODO Not correct currently, need to ask about how to send it to frontend


def game_create(event):
    #make random game code
    code = random.randbits(32).hex()
    #checks five times then if failed to generate a unique code, returns an error
    for _ in range(5):
        if code not in game_codes:
            break
        code = random.randbits(32).hex()
    else:
        return {"code": -1}
    
    try:
        connection = _get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO games (casual) VALUES (%s)",
                    (True,),
                )
                game_id = cursor.lastrowid  # Get the auto-incremented id
            connection.commit()
        finally: 
            connection.close()
    except MySQLError:
        return {"code": -1}
    empty_seats = [Player(name="", is_bot=False) for _ in range(6)]
    games[game_id] = {"game": Game(empty_seats), "code": code}
    game_codes[code] = game_id
    return {"code": 0, "game_code": code}

def create_ranked_game(matched_players: list[str]) -> str:
    """Create a ranked game with the matched players already seated."""
    # Insert into database
    try:
        connection = _get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO games (player_count, ranked) VALUES (%s, %s)",
                    (len(matched_players), True),
                )
                game_id = cursor.lastrowid  # Get the auto-incremented id
            connection.commit()
        finally: 
            connection.close()
    except MySQLError:
        return {"code": -1}
    
    # Create game with matched players seated
    player_list = []
    for i in range(len(matched_players)):
        player_list.append(Player(name=matched_players[i], is_bot=False))
    
    games[game_id] = Game(player_list)
    return game_id

def game_join(event):
    username = event.get("name")
    if not isinstance(username, str) or not username.strip():
        return {"code": 4}
    username = username.strip()

    code = event.get("game_code")
    if isinstance(code, str):
        # Look up game_id from game_code
        game_id = game_codes.get(code)
        if game_id is None:
            return {"code": 1}  # Game not found
    elif isinstance(code, int):
        # Direct game_id
        game_id = code
    else:
        return {"code": 2}  # Invalid type
    
    game_entry = games.get(game_id)
    if game_entry is None:
        return {"code": 1}
    
    game = game_entry["game"]
    player_list = game.player_list

    for player in player_list:
        if player.name == username:
            return {"code": 5}
    for i, player in enumerate(player_list):
        if player.name == "":
            player_list[i] = Player(name=username, is_bot=False)
            return {"code": 0}
    
    return {"code": 5}


    

def game_modify(event):
    pass

def move(event):
    pass


# SERVER MESSAGES
def game_state():
    pass

def game_settings():
    pass

def game_results():
    pass
   