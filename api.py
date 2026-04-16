import base64
import hashlib
import os
import re
import random

import pymysql
from pymysql import IntegrityError, MySQLError

from game import Game, Player

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

games: dict[int, Game] = {}
# TODO: make the API functions actually do stuff

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


def game_request(event):
    pass


def game_create(event):
    #make random game code
    code = random.randbits(32).hex()
    #checks five times then if failed to generate a unique code, returns an error
    for _ in range(5):
        if code not in games:
            break
    else:
        return {"code": -1}
    
    try:
        connection = _get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO games (code) VALUES (%s)",
                    (code,),
                )
            connection.commit()
        finally: 
            connection.close()
    except MySQLError:
        return {"code": -1}
    empty_seats = [Player(name="", is_bot=False) for _ in range(6)]
    games[code] = Game(empty_seats)
    return {"code": 0, "game_code": code}

def game_join(event):
    username = event.get("name")
    if not isinstance(username, str) or not username.strip():
        return {"code": 4}
    username = username.strip()

    code = event.get("game_code")
    if not isinstance(code,int):
        return {"code": 2}
    
    game = games.get(code)
    if game is None:
        return {"code": 1}
    
    player_list = game.player_list

    for player in player_list:
        if player.name == username:
            return {"code": 5}
    for i,player in enumerate(player_list):
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

   