from discord.ext import commands
import discord
import aiopypixel


class Player(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        self.hypixel = aiopypixel.Client(self.bot.hypixel_key)

    @commands.command(name="friends", aliases=["pfriends", "playerfriends", "friendsof"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def player_friends(self, ctx, player):
        player_friends = await self.hypixel.getPlayerFriends(player)
        if not player_friends:
            await ct


def setup(bot):
    bot.add_cog(Player(bot))