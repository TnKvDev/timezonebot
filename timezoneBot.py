import asyncio
from os import environ

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
token = environ["TZ_BOT_TOKEN"]

intents = discord.Intents.default()
intents.message_content = True

description="This bot is there to manage timezones of the server members."
bot = commands.Bot(command_prefix=',', description=description, intents=intents)

@bot.event
async def on_ready():
    print(f'logged in as {bot.user}')

async def load_extensions():
    await bot.load_extension("cogs.tz_cog")

async def main():
    async with bot:
        await load_extensions()
        await bot.start(token)

asyncio.run(main())
