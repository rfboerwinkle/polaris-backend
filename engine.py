# This file provides helper functions for interfacing with the backend engine.

import asyncio

stdio_lock = asyncio.Lock()

async def make_bot_move(game:Game) -> None:
    pass
