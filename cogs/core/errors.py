import discord
import traceback
from random import choice
from ..core.cache import *
from discord.ext import commands
from aiopypixel.exceptions.exceptions import *


class Errors(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def send(self, ctx, msg):
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

        try:
            await self.send(ctx, str(e))

            if isinstance(e.original, RateLimitError):
                await self.send(ctx, f"Uh oh, something took way too long, try again! If this message persists, "
                                     f"please contact us on the [support server](https://discord.gg/{self.bot.guild_invite_code}), thank you!")
                return

            elif "NoStatError" in str(e):
                await self.send(ctx, "No stats available!")
                return

            elif isinstance(e.original, InvalidPlayerError):
                await self.send(ctx, "That player is invalid or doesn't exist!")
                return

            elif isinstance(e.original, InvalidGuildError):
                await self.send(ctx, "That guild is invalid or doesn't exist!")
                return

            elif isinstance(e.original, NullPlayerError):
                await self.send(ctx, "That player hasn't joined Hypixel before! (They don't have any stats!)")
                return

            elif isinstance(e.original, InvalidDiscordUser):
                await self.send(ctx, "That user doesn't have their account linked, or doesn't exist!\nIf you'd like to link your account, do `h!link <mc_username>`")
                return

        except AttributeError:
            pass

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

        # Commands to ignore
        for _type in [commands.CommandNotFound, commands.NotOwner, commands.CheckFailure, discord.errors.Forbidden]:
            if isinstance(e, _type):
                return

        if isinstance(e, commands.MaxConcurrencyReached):
            await self.send(ctx, "Hold on! You can't use multiple of that command at once!")
            return

        if isinstance(e, commands.CommandOnCooldown):
            descs = [
                "Didn't your parents tell you [patience is a virtue](http://www.patience-is-a-virtue.org/)? Calm down and wait another {0} seconds.",
                "Hey, you need to wait another {0} seconds before doing that again.",
                "Hrmmm, looks like you need to wait another {0} seconds before doing that again.",
                "Don't you know [patience was a virtue](http://www.patience-is-a-virtue.org/)? Wait another {0} seconds."
            ]

            await self.send(ctx, choice(descs).format(round(e.retry_after, 2)))
            return
        else:
            ctx.command.reset_cooldown(ctx)

        if isinstance(e, commands.errors.MissingRequiredArgument):
            await self.send(ctx, "Looks like you're forgetting to put something in!")
            return

        if isinstance(e, commands.BadArgument):
            await self.send(ctx, "Looks like you typed something wrong, try typing it correctly the first time, idiot.")
            return

        if "error code: 50013" in str(e):
            await self.send(ctx, "I can't do that, you idiot.")
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

            await self.send(error_channel, f"```{ctx.author}: {ctx.message.content}\n\n{traceback_text}```")


def setup(bot):
    bot.add_cog(Errors(bot))
