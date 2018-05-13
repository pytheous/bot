import logging
import os
import socket

from aiohttp import AsyncResolver, ClientSession, TCPConnector
from discord import Game
from discord.ext.commands import AutoShardedBot, when_mentioned_or

from bot.constants import CLICKUP_KEY, DEBUG_MODE
from bot.formatter import Formatter

log = logging.getLogger(__name__)

bot = AutoShardedBot(
    command_prefix=when_mentioned_or(
        "self.", "bot."
    ),
    activity=Game(
        name="Help: bot.help()"
    ),
    help_attrs={
        "name": "help()",
        "aliases": ["help"]
    },
    formatter=Formatter(),
    case_insensitive=True
)

# Global aiohttp session for all cogs - uses asyncio for DNS resolution instead of threads, so we don't *spam threads*
if DEBUG_MODE:
    bot.http_session = ClientSession(
        connector=TCPConnector(
            resolver=AsyncResolver(),
            family=socket.AF_INET,  # Force aiohttp to use AF_INET if this is a local session. Prevents crashes.
            verify_ssl=False,
        )
    )
else:
    bot.http_session = ClientSession(connector=TCPConnector(resolver=AsyncResolver()))

# Internal/debug
bot.load_extension("bot.cogs.logging")
bot.load_extension("bot.cogs.security")
bot.load_extension("bot.cogs.events")


# Commands, etc
bot.load_extension("bot.cogs.bot")
bot.load_extension("bot.cogs.cogs")

# Local setups usually don't have the clickup key set,
# and loading the cog would simply spam errors in the console.
if CLICKUP_KEY is not None:
    bot.load_extension("bot.cogs.clickup")
else:
    log.warning("`CLICKUP_KEY` not set in the environment, not loading the ClickUp cog.")

bot.load_extension("bot.cogs.deployment")
bot.load_extension("bot.cogs.eval")
bot.load_extension("bot.cogs.fun")
bot.load_extension("bot.cogs.hiphopify")
bot.load_extension("bot.cogs.tags")
bot.load_extension("bot.cogs.verification")

bot.run(os.environ.get("BOT_TOKEN"))

bot.http_session.close()  # Close the aiohttp session when the bot finishes running
