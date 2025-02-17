import threading
import asyncio

from discord_bot import DiscordBot

class BotThread(threading.Thread):
    def __init__(self, bot: DiscordBot):
        super().__init__(daemon=True)
        self.bot = bot

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.bot.run())