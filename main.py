import asyncio
from json import dumps,loads

from websockets.asyncio.server import serve

import api

# TODO: handle api requests that result in broadcasted messages

# returns a dictionary with type, id, code, and any other necessary info.
# done outside of handler function to not worry about asyncio stuff.
def handle_message(message):
    # assuming messages are sent/recieved in JSON format
    ret = {"type":"ack", "id":0, "code":-1}
    try:
        event = loads(message)
    except:
        ret["code"] = 2
        return ret
    # ensure id is an int
    if type(event["id"]) != int:
        ret["code"] = 2
        ret["id"] = 0
        return ret
    else:
        ret["id"] = event["id"]

    # the JSON object will be passed into all api.py functions
    # api func should return a dictionary including code, NOT type or id
    # TODO: Server messages?
    try:
        if event["type"] == "signup":
            ret.update(api.signup(event))
        elif event["type"] == "login":
            ret.update(api.login(event))
        elif event["type"] == "game_request":
            ret.update(api.game_request(event))
        elif event["type"] == "game_create":
            ret.update(api.game_create(event))
        elif event["type"] == "game_join":
            ret.update(api.game_join(event))
        elif event["type"] == "game_modify":
            ret.update(api.game_modify(event))
        elif event["type"] == "move":
            ret.update(api.move(event))
        else:
            ret["code"] = 2
    finally:
        return ret


async def handler(websocket):
    async for message in websocket:
        # print("incoming: " + str(message))
        outgoing = handle_message(message)
        # print("outgoing: " + str(outgoing))
        await websocket.send(dumps(outgoing))



async def main():
    # maybe change the port number?
    async with serve(handler, "", 2122) as server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
