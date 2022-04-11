#!/usr/bin/env python

import aioredis


class PsychoStats():
    def __init__(self, db):
        self.r = aioredis.from_url("redis://localhost", db=db, decode_responses=True)

    async def test(self):
        for i in range(10):
            await self.r.xadd('ind1', {'t': i, 'h': i})
            await self.r.xadd('ind2', {'t': i, 'h': i})
            await self.r.xadd('ind3', {'t': i, 'h': i})
            await self.r.xadd('ind4', {'t': i, 'h': i})
            await self.r.xadd('ind5', {'t': i, 'h': i})
            await self.r.xadd('ind6', {'t': i, 'h': i})
            await self.r.xadd('ind7', {'t': i, 'h': i})
            await self.r.xadd('ind8', {'t': i, 'h': i})

    # cur = "0"  # set initial cursor to 0
    # while cur:
    #     cur, keys = await redis.scan(cur)
    #     print("Iteration results:", keys)
