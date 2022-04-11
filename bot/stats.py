#!/usr/bin/env python

import enum
import aioredis


class ActionStatus(enum.Enum):
    start = 1
    help = 2
    rules = 3
    request_card = 4
    send_card = 5


class PsychoStats():
    def __init__(self, db):
        self.r = aioredis.from_url("redis://localhost", db=db, decode_responses=True)

    async def add_action(self, id, action, result):
        await self.r.xadd("stats:{0}".format(id), {'a': action.value, 'r': result})

    # cur = "0"  # set initial cursor to 0
    # while cur:
    #     cur, keys = await redis.scan(cur)
    #     print("Iteration results:", keys)
