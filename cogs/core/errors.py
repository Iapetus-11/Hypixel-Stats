import discord
import traceback
from aiopypixel.exceptions.exceptions import *
from discord.ext import commands
from random import choice

from ..core.cache import *


class Errors(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def send(self, ctx, msg):
        try:
            await ctx.send(embed=discord.Embed(color=await self.bot.cc(ctx.author.id), description=msg))
        except discord.errors.Forbidden:
            pass
        except Exception:
            try:
                await ctx.send(embed=discord.Embed(color=await self.bot.cc(), description=msg))
            except discord.errors.Forbidden:
                pass

    @commands.Cog.listener()
    async def on_command_error(self, ctx, e):
        try:
            if ctx.handled is None:
                ctx.handled = False
        except AttributeError:
            ctx.handled = False

        # Commands to ignore
        for _type in [commands.CommandNotFound, commands.NotOwner, commands.CheckFailure, discord.errors.Forbidden]:
            if isinstance(e, _type):
                return

        if isinstance(e, commands.MaxConcurrencyReached):
            await self.send(ctx, "Hold on! You can't use multiple of that command at once!")
            return

        if isinstance(e, commands.CommandOnCooldown):
            if await self.bot.get_cog("Database").is_premium(ctx.author.id):
                e.retry_after -= (2 / 3) * e.cooldown.per

            if round(e.retry_after, 2) == 0:
                await ctx.reinvoke()

            descs = [
                "Didn't your parents tell you that [patience is a virtue](http://www.patience-is-a-virtue.org/)? Calm down and wait another {0} seconds.",
                "Hey, you need to wait another {0} seconds before doing that again.",
                "Hrmmm, looks like you need to wait another {0} seconds before doing that again.",
                "Don't you know [patience is a virtue](http://www.patience-is-a-virtue.org/)? Wait another {0} seconds."
            ]

            await self.send(ctx, choice(descs).format(round(e.retry_after, 2)))
            return

        if isinstance(e, commands.errors.MissingRequiredArgument):
            await self.send(ctx, "Looks like you're forgetting to put something in!")
            return

        if isinstance(e, commands.BadArgument):
            await self.send(ctx, "Looks like you typed something wrong.")
            return

        if isinstance(e, commands.errors.NoPrivateMessage):
            await self.send(ctx, "This command can't be used in private chat channels.")
            return

        if isinstance(e, commands.MissingPermissions):
            await self.send(ctx, "Nice try, but you don't have the permissions to do that.")
            return

        if isinstance(e, commands.CheckAnyFailure):
            if "MissingPermissions" in str(e.errors):  # yes I know this is jank but it works so shhhh
                await self.send(ctx, "Nice try, but you don't have the permissions to do that.")
                return

        if isinstance(e, commands.BotMissingPermissions):
            await self.send(ctx, "You didn't give me proper the permissions to do that!")
            return

        if "NoStatError" in str(e):
            await self.send(ctx, "No stats available!")
            return

        if isinstance(e.original, RateLimitError):
            await self.send(ctx, f"Uh oh, something took way too long, try again! If this message persists, "
                                 f"please contact us on the [support server](https://discord.gg/{self.bot.guild_invite_code}), thank you!")
            return

        if isinstance(e.original, InvalidPlayerError) or isinstance(e, InvalidPlayerError):
            await self.send(ctx, "That player is invalid or doesn't exist!")
            return

        if isinstance(e.original, InvalidGuildError):
            await self.send(ctx, "That guild is invalid or doesn't exist!")
            return

        if isinstance(e.original, NullPlayerError):
            await self.send(ctx, "That player hasn't joined Hypixel before! (They don't have any stats!)")
            return

        if isinstance(e.original, InvalidDiscordUser) or isinstance(e,
                                                                    InvalidDiscordUser) or "InvalidPlayerError" in str(
            e):
            await self.send(ctx,
                            "That user doesn't have their account linked, or doesn't exist!\nIf you'd like to link your account, do `h!link <mc_username>`")
            return

        if "error code: 50013" in str(e):
            await self.send(ctx, "I can't do that, you idiot.")
            return

        if "HypixelsFault" in str(e):
            await self.send(ctx, "Uh Oh! It looks like Hypixel's API is having some trouble right now...")
            return

        if "HTTPException: 503 Service Unavailable (error code: 0)" not in str(
                e) and "discord.errors.Forbidden" not in str(e):
            await self.send(ctx, f"**Unknown Error.** The error has been magically broadcasted to our support "
                                 f"team. If this bug continues, please report it on our "
                                 f"[support server](https://discord.gg/{self.bot.guild_invite_code})")

            error_channel = self.bot.get_channel(self.bot.error_channel_id)

            # Thanks TrustedMercury!
            # yw
            etype = type(e)
            trace = e.__traceback__
            verbosity = 4
            lines = traceback.format_exception(etype, e, trace, verbosity)
            traceback_text = ''.join(lines)

            traceback_text = traceback_text[:1023]

            if "discord.errors.Forbidden" in traceback_text:
                try:
                    await self.send(ctx, "It looks like I don't have the proper permissions to do this!")
                except Exception:
                    pass
                return

            await self.send(error_channel, f"```{ctx.author}: {ctx.message.content}\n\n{traceback_text}```")


def setup(bot):
    bot.add_cog(Errors(bot))
