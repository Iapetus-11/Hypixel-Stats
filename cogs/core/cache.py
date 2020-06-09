import aiohttp
import aiopypixel
import asyncio
import discord
from discord.ext import commands


class Cache(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.hypixel = aiopypixel.Client(self.bot.hypixel_key)

        self.session = aiohttp.ClientSession()

        self.valid_names_and_uuids = []  # clear every hour or so
        self.name_uuid_cache = {}  # {name: uuid} clear this maybe twice a day?
        self.uuid_name_cache = {}  # {uuid: name} clear this maybe twice a day?
        self.player_friends_cache = {}  # {uuid: [friends...]} clear this every 2 hrs
        self.player_guild_cache = {}  # {uuid: guild} clear every 1 hr
        self.guild_id_name_cache = {}  # {id: name} for guilds, clear every day or somethin
        self.player_object_cache = {}  # {uuid: Player} every thirty min?
        self.player_pfp_cache = {}  # {uuid: pfp in b64} every 2 days or somethin

    def cog_unload(self):
        self.bot.loop.create_task(self.session.close())

    async def get_player_uuid(self, player):
        if len(player) > 16:
            if player in self.valid_names_and_uuids:
                return player

        uuid = self.name_uuid_cache.get(player)

        if uuid is None:
            uuid = await self.hypixel.usernameToUUID(player)
            self.name_uuid_cache[player] = uuid

        if uuid not in self.valid_names_and_uuids:
            self.valid_names_and_uuids.append(uuid)
        return uuid

    async def get_player_name(self, player):
        if len(player) <= 16:
            if player in self.valid_names_and_uuids:
                return player

        name = self.uuid_name_cache.get(player)

        if name is None:
            name = await self.hypixel.UUIDToUsername(player)
            self.uuid_name_cache[player] = name

        if name not in self.valid_names_and_uuids:
            self.valid_names_and_uuids.append(name)
        return name

    async def rate_limit_wait(self, to_be_awaited):
        try_again = True
        while try_again:
            try:
                awaited = await to_be_awaited
                try_again = False
            except aiopypixel.exceptions.exceptions.RateLimitError:
                await asyncio.sleep(self.bot.ratelimited_wait_time)
        return awaited

    async def get_player_friends(self, player):
        player = await self.get_player_uuid(player)  # ensure it's a uuid for best caching results

        friends = self.player_friends_cache.get(player)

        if friends is None:
            friends = await self.rate_limit_wait(self.hypixel.getPlayerFriends(player))
            self.player_friends_cache[player] = friends
        return friends

    async def get_player_guild(self, player):
        player = await self.get_player_uuid(player)

        guild_id = self.player_guild_cache.get(player)

        if guild_id is None:
            guild_id = await self.rate_limit_wait(self.hypixel.getPlayerGuild(player))
            self.player_guild_cache[player] = guild_id
        return guild_id

    async def get_guild_name_from_id(self, guild_id):
        guild_name = self.guild_id_name_cache.get(guild_id)

        if guild_name is None:
            guild_name = await self.rate_limit_wait(self.hypixel.getGuildNameByID(guild_id))
            self.guild_id_name_cache[guild_id] = guild_name
        return guild_name

    async def get_player(self, player):  # uuid preferred
        player = await self.get_player_uuid(player)

        player_object = self.player_object_cache.get(player)

        if player_object is None:
            player_object = await self.rate_limit_wait(self.hypixel.getPlayer(player))
            self.player_object_cache[player] = player_object
        return player_object

    async def get_player_head(self, player):
        player = await self.get_player_uuid(player)
        return f"https://crafatar.com/avatars/{player}"


def setup(bot):
    bot.add_cog(Cache(bot))
