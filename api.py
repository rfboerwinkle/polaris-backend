import base64
import hashlib
import os
import re
import random

import pymysql
from pymysql import IntegrityError, MySQLError

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
    username = event.get("name")
    password = event.get("pass")

    player_c = event.get("player_count",2)
    casual = event.get("casual", True)
    ranked = event.get("ranked", False)   
    time_limit = event.get("time_limit", 0)
    increment = event.get("increment", 0)
    
    if user_validate(event) == 4:
        return {"code": 4}

    try:   
        connection = _get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT id,password_hash, salt FROM users WHERE name = %s",
                    (username,),
                )
                user = cursor.fetchone()
                if user is None:
                    return {"code": 4}

                stored_hash = user["password_hash"]
                salt = base64.b64decode(user["salt"])

                computed_hash, _ = _hash_password(password, salt)
                if computed_hash != stored_hash:
                    return {"code": 4}
                
                user_id = user["id"]
                #just makes a random game ID will probably change later but for testing this should be fine
                extern_id = random.getrandbits(63)

                cursor.execute("""
                    INSERT INTO games (extern_id, player_count, casual, ranked, time_limit, increment,casual,ranked)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (extern_id, player_c, casual, ranked, time_limit, increment, casual, ranked))
                game_id = cursor.lastrowid

                cursor.execute("""
                    INSERT INTO game_players (game_id, user_id, player_number)
                    VALUES (%s, %s, %s)
                """, (game_id, user_id, 1))
                return {"code": 0, "game_id": extern_id}
        finally:
            connection.close()
    except MySQLError:
        return {"code": -1}
    except IntegrityError:
        return {"code": 5}


def game_join(event):
    username = event.get("name")
    password = event.get("pass")
    external_id = event.get("external_id")
    if user_validate(event) == 4:
        return {"code": 4}
    try:
        connection = _get_connection()
        try:
            with connection.cursor() as cursor:

                cursor.execute(
                    "SELECT id, password_hash, salt FROM users WHERE name = %s",
                    (username,),
                )
                user = cursor.fetchone()

                if user is None:
                    return {"code": 4}

                stored_hash = user["password_hash"]
                salt = base64.b64decode(user["salt"])
                computed_hash, _ = _hash_password(password, salt)

                if computed_hash != stored_hash:
                    return {"code": 4}

                user_id = user["id"]

                cursor.execute(
                    "SELECT id, player_count FROM games WHERE external_id = %s",
                    (external_id,),
                )
                game = cursor.fetchone()

                if game is None:
                    return {"code": 4}

                game_id = game["id"]
                max_players = game["player_count"]

                cursor.execute(
                    "SELECT user_id, player_number FROM players WHERE game_id = %s",
                    (game_id,),
                )
                players = cursor.fetchall()

                for p in players:
                    if p["user_id"] == user_id:
                        return {"code": 5}

                if len(players) >= max_players:
                    return {"code": 5}

                taken_numbers = {p["player_number"] for p in players}
                player_number = 1
                while player_number in taken_numbers:
                    player_number += 1

                cursor.execute(
                    """
                    INSERT INTO players (game_id, user_id, player_number)
                    VALUES (%s, %s, %s)
                    """,
                    (game_id, user_id, player_number),
                )

            connection.commit()

            return {
                "code": 0,
                "game_id": game_id,
                "player_number": player_number
            }

        finally:
            connection.close()

    except IntegrityError:
        return {"code": 5}
    except MySQLError:
        return {"code": -1}
  

def game_modify(event):
  pass

def move(event):
  pass


# SERVER MESSAGES
def game_state():
  pass

def user_validate(event):
    username = event.get("name")
    password = event.get("pass")
    external_id = event.get("external_id")

    # Validate input
    if not isinstance(username, str):
        return {"code": 4}

    username = username.strip()
    if not USERNAME_RE.fullmatch(username):
        return {"code": 4}

    if not isinstance(password, str):
        return {"code": 4}

    if not (PASSWORD_MIN_LENGTH <= len(password) <= PASSWORD_MAX_LENGTH):
        return {"code": 4}

    if not isinstance(external_id, int):
        return {"code": 4}

