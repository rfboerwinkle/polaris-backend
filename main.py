import asyncio
from json import dumps,loads

from websockets.asyncio.server import serve

import api


game_conns: dict[int, set] = {}
def add_conn(game_id:int,websocket) -> None:
    game_conns.setdefault(game_id, set()).add(websocket)

def rem_conn(game_id:int,websocket) -> None:
    if game_id in game_conns:
        game_conns[game_id].discard(websocket)
        if not game_conns[game_id]:
            del game_conns[game_id]
# TODO: handle api requests that result in broadcasted messages

# Periodically check for matchmaking for ranked queue
async def matchmaking_loop():
    while True:
        try:
            matched = await api.ranked_queue.try_match()
            if matched:
                print(f"Match found: {matched}")
                game_code = api.create_ranked_game(matched)
                print(f"Created ranked game: {game_code}")
        except Exception as e:
            print(f"Error in matchmaking loop: {e}")
        await asyncio.sleep(2)  # Check every 2 seconds

# returns a dictionary with type, id, code, and any other necessary info.
# done outside of handler function to not worry about asyncio stuff.
async def handle_message(message, logged_in_user,current_game_id=None,websocket=None):
    # assuming messages are sent/recieved in JSON format
    ret = {"type":"ack", "id":0, "code":-1}
    try:
        event = loads(message)
    except:
        ret["code"] = 2
        return ret,logged_in_user
    
    # ensure id is an int
    if type(event["id"]) != int:
        ret["code"] = 2
        ret["id"] = 0
        return ret,logged_in_user
    else:
        ret["id"] = event["id"]

    # the JSON object will be passed into all api.py functions
    # api func should return a dictionary including code, NOT type or id
    # TODO: Server messages?
    try:
        if event["type"] == "signup":
            ret.update(api.signup(event))


        elif event["type"] == "login":
            res = api.login(event)
            ret.update(res)
            if res["code"] == 0:
                logged_in_user = event.get("name", "").strip()
        
        
        elif event["type"] == "game_request":
            if logged_in_user is None:
                ret["code"] = 3
            else:
                event["name"] = logged_in_user
                ret.update(await api.game_request(event))
        
        
        elif event["type"] == "game_create":
            #Gharret: get game id 
            if logged_in_user is None:
                ret["code"] = 3
            else:
                res = api.game_create(event)
                ret.update(res)
                if res["code"] == 0:
                    event["game_id"] = res["game_id"]
                    add_conn(event["game_id"], websocket)
        
        
        elif event["type"] == "game_join":
            #add game_id to pass so user
            if logged_in_user is None:
                ret["code"] = 3
            else:
                event["name"] = logged_in_user
                ret.update(api.game_join(event))
                if ret["code"] == 0:
                    if current_game_id is not None:
                        rem_conn(current_game_id, websocket)
                    current_game_id = res["game_id"]
                    add_conn(current_game_id, websocket)
       
       
        elif event["type"] == "game_modify":
            if logged_in_user is None:
                ret["code"] = 3
            elif current_game_id is None:
                ret["code"] = 1
            else:
                event["name"] = logged_in_user
                event["game_id"] = current_game_id
                ret.update(await api.game_modify(event,game_conns))
       
       
        elif event["type"] == "move":
            if logged_in_user is None:
                ret["code"] = 3
            elif current_game_id is None:
                ret["code"] = 1
            else:
                event["name"] = logged_in_user
                event["game_id"] = current_game_id
                ret.update(await api.move(event,game_conns))
        
        else:
            ret["code"] = 2
    finally:
        return ret, logged_in_user,current_game_id


async def handler(websocket):
    logged_in_user = None
    current_game_id = None
    try:
        async for message in websocket:
            # print("incoming: " + str(message))
            outgoing, logged_in_user, current_game_id = await handle_message(
                            message, logged_in_user, current_game_id, websocket
                        )            # print("outgoing: " + str(outgoing))
            await websocket.send(dumps(outgoing))
    finally:
        if current_game_id is not None:
            rem_conn(current_game_id, websocket)


async def main():
    # maybe change the port number?
    matchmaking_task = asyncio.create_task(matchmaking_loop())
    async with serve(handler, "", 2122) as server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
