from discord.ext import commands
import discord
import aiopypixel
import asyncio


class Cache(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.hypixel = aiopypixel.Client(self.bot.hypixel_key)

        self.valid_names_and_uuids = []  # clear once a day

        self.name_uuid_cache = {}  # {name: uuid} clear this maybe once a day?
        self.uuid_name_cache = {}  # {uuid: name} clear this maybe once a day?

        self.player_friends_cache = {}  # {uuid: [friends...]} clear this every 2 hrs

    async def get_player_uuid(self, player):
        if len(player) <= 16:
            if player in self.valid_names_and_uuids:
                return player

        uuid = self.name_uuid_cache.get(player)

        if uuid is None:
            uuid = await self.hypixel.UsernameToUUID(player) # should be lowercause u username not Username but yeah
            self.name_uuid_cache[player] = uuid

        if uuid not in self.valid_names_and_uuids:
            self.valid_names_and_uuids.append(uuid)

        return uuid

    async def get_player_name(self, player):
        if len(player) > 16:
            if player in self.valid_names_and_uuids:
                return player

        name = self.uuid_name_cache.get(player)

        if name is None:
            name = await self.hypixel.usernameToUUID(player)
            self.uuid_name_cache[player] = name

        if name not in self.valid_names_and_uuids:
            self.valid_names_and_uuids.append(name)

        return name

    async def get_player_friends(self, player):
        player = await self.get_player_uuid(player) # ensure it's a uuid for best caching results

        friends = player_friends_cache.get(player)

        if friends is None:
            try_again = True
            while try_again:
                try:
                    friends = await self.hypixel.getPlayerFriends(player)
                    try_again = False
                except aiopypixel.exceptions.exceptions.RateLimitError:
                    await asyncio.sleep(self.bot.ratelimited_wait_time)

            self.player_friends_cache[player] = friends

        return friends
