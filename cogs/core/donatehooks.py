import arrow
import asyncio
import discord
from aiohttp import web
from discord.ext import commands


class DonateHooks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.db = self.bot.get_cog("Database")

        self.hook = self.bot.loop.create_task(self.donatebot_hook())

    def cog_unload(self):
        self.hook.cancel()

    async def donatebot_hook(self):

        async def handler(r):
            if r.headers.get("authorization") == self.bot.donatebot_auth_secret:
                jj = await r.json()

                # kuINi_O9Vq = Premium Monthly Subscription product id (currently 2.99$)
                if jj.get("product_id") == "kuINi_O9Vq":
                    if jj.get("buyer_id") is not None:
                        if jj.get("status") == "completed":
                            await self.bot.get_channel(732658675725893743).send(
                                f"Payment completed! USER ID: {jj.get('buyer_id')} TXN_ID: {jj.get('txn_id')} Time: {arrow.utcnow().timestamp}")
                            timestamp_ends = arrow.utcnow().shift(weeks=+4).timestamp
                            await self.db.set_premium(int(jj.get("buyer_id")), timestamp_ends)
                            return web.Response()
                        elif jj.get("status") in ["reversed", "refunded", "sub_ended"]:
                            await self.bot.get_channel(732658675725893743).send(
                                f"Payment not completed. Status: ({jj.get('status')}) USER ID: {jj.get('buyer_id')} TXN_ID: {jj.get('txn_id')} Time: {arrow.utcnow().timestamp}")
                            await self.db.remove_premium(int(jj.get("buyer_id")))
                            return web.Response()
                return web.Response(status=406)
            return web.Response(status=401)

        app = web.Application(loop=self.bot.loop)
        app.router.add_view("/donatebot", handler)

        runner = web.AppRunner(web_app)
        await runner.setup()

        site = web.TCPSite(runner, "0.0.0.0")
        await site.start()


def setup(bot):
    bot.add_cog(DonateHooks(bot))
