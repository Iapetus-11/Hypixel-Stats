from discord.ext import commands
import discord
import aiopypixel


class Player(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        self.cache = self.bot.get_cog("Cache")

    @commands.command(name="friends", aliases=["pfriends", "playerfriends", "friendsof"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def player_friends(self, ctx, player):
        await ctx.trigger_typing()

        try:
            player_friends = await self.cache.get_player_friends(player)
        except aiopypixel.exceptions.exceptions.InvalidPlayerError:
            await ctx.send(embed=discord.Embed(color=self.bot.cc, description="That player is invalid or doesn't exist!"))
        else:
            if not player_friends:
                await ctx.send(embed=discord.Embed(color=self.bot.cc, description=f"{player} doesn't have any friends! :cry:"))

            embed = discord.Embed(color=self.bot.cc, title=f"``{player}``'s friends ({len(player_friends)} total!)")

            body = ""
            count = 0
            for friend in player_friends:
                try:
                    name = await self.cache.get_player_name(friend)
                except aiopypixel.exceptions.exceptions.InvalidPlayerError:
                    name = "Unknown User"
                body += f"{name}\n"
                if count > 20:
                    embed.add_field(name="\uFEFF", value=body)
                    count = 0
                    body = ""
                count += 1
            if count > 0:
                embed.add_field(name="\uFEFF", value=body)

            if len(embed) > 5095:
                await ctx.send(embed=discord.Embed(color=self.bot.cc, description="That user has too many friends to show!"))
                return

            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Player(bot))
