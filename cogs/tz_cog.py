from datetime import datetime as dt
from typing import Optional
from zoneinfo import ZoneInfo

import discord
from discord.ext import commands

from database import database

db = database(path_to_db_file="./userTimezone.sql")

# idk what to name this array lowkey
timezone_continents = [
    "Africa", "America", "Antarctica", "Asia", "Australia",
    "Brazil", "Canada", "Chile", "Europe", "Indian", "Mexico",
    "Pacific", "US", "Etc"
]

async def send_embed(ctx, description, custom_embed: Optional[discord.Embed] = None):
    embed = discord.Embed(
        description=description, color=0x7F00FF
    )

    no_ping = discord.AllowedMentions(users=False, roles=False, everyone=False)
    if custom_embed is None:
        await ctx.reply(embed=embed, allowed_mentions=no_ping)
    else:
        await ctx.reply(embed=custom_embed, allowed_mentions=no_ping)

def make_it_valid(input_str: str) -> str | None:
    # If only e.g the city is been given for input,
    # the bot will append every continent to the city
    # in the IANA timezone format and check for validation
    corrected = input_str.capitalize()

    # The upcoming part is for specific cities that
    # have spaces in their name, for example:
    # New York would be written as New_York.
    # This while loop will look for underscores
    # and capitalize the letters coming after.
    if "_" in corrected:
        corrected_str_list = list(corrected)
        i = 0
        while i < len(corrected_str_list) - 1:
            if corrected_str_list[i] == '_':
                corrected_str_list[i + 1] = corrected_str_list[i + 1].upper()
            i += 1
        corrected = "".join(corrected_str_list)

    for zone in timezone_continents:
        corrected_zone = zone + "/" + corrected
        if validate_timezone(corrected_zone):
            return corrected_zone

    return None

def validate_timezone(input_str: str) -> bool:
    try:
        dt.now(ZoneInfo(input_str))
        print("Success: valid timezone found!")
    except Exception as e:
        print(f'Error: Timezone doesnt exist: {e}')
        return False
    return True

class tzCog(commands.Cog, name='tz'):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name='tz', invoke_without_command=True)
    async def tz(self, ctx, user: Optional[str] = None):
        target = ctx.author
        if user is not None:
            try:
                target = await commands.MemberConverter().convert(ctx, user)
            except commands.MemberNotFound:
                await send_embed(ctx, f'<@{ctx.author.id}>: Could not find that user... provide a user name, mention, or ID')
                return

        zone_str = db.get_timezone(target.id)


        if zone_str is None:
            if not user:
                await send_embed(ctx, f"<@{ctx.author.id}>: You dont have a timezone set")
            else:
                await send_embed(ctx, f'<@{ctx.author.id}>: {target.name} doesnt have a timezone set')
            return

        time = dt.now(ZoneInfo(zone_str))
        # time_formatted = time.strftime('%B %d, %H:%M')
        timeformat_config = db.get_timeformat_config(target.id)
        print(timeformat_config)
        time_formatted = None
        match timeformat_config:
            case 24:
                time_formatted = time.strftime('%B %d, %H:%M')
            case 12:
                time_formatted = time.strftime('%B %d, %I:%M %p')
            case 1:
                time_formatted = time.strftime('%Y-%m-%dT%H:%M')

        if not user:
            await send_embed(ctx, f'<@{ctx.author.id}>: Your time is **{time_formatted}**')
        else:
            await send_embed(ctx, f'<@{ctx.author.id}>: {target.name}\'s time is **{time_formatted}**')

    @tz.command(name='set', brief='sets your timezone')
    async def set(self, ctx, timezone: str):
        if validate_timezone(timezone):
            db.write_timezone(ctx.author.id, timezone)
            await send_embed(ctx, f'<@{ctx.author.id}>: Timezone set to **{timezone}**')
        else:
            valid_zone = make_it_valid(timezone)
            if valid_zone is not None:
                db.write_timezone(ctx.author.id, valid_zone)
                await send_embed(ctx, f'<@{ctx.author.id}>: Timezone set to **{valid_zone}**')
            else:
                await send_embed(ctx, f'<@{ctx.author.id}>: Invalid Timezone')

    @tz.command(name='setFormat', brief='set timeformat config')
    async def setFormat(self, ctx, desired_format: int | str):
        timeformat = None
        match desired_format:
            case 24:
                timeformat = 24
            case 12:
                timeformat = 12
            case "iso":
                timeformat = 1
            case _:
                await send_embed(ctx, f'<@{ctx.author.id}>: Invalid Format... Available formats: 24, 12, iso')
                return

        db.write_timeformat_config(ctx.author.id, timeformat)
        await send_embed(ctx, f'<@{ctx.author.id}>: Format set to {timeformat if timeformat != 1 else "iso"}')

    # todo: implement
    @tz.command(name='into', brief='Get the time of an user at a specific time of yours')
    async def into(self, ctx)

    # @tz.command(name='get', brief='get your timezone')
    # async def get(self, ctx, user: Optional[discord.Member]=None):
    #     if not user:
    #         zone = db.get_timezone(ctx.author.id)
    #         if zone is None:
    #             await send_embed(ctx, 'You dont have a timezone set')
    #             return
    #         else:
    #             await send_embed(ctx, f'<@{ctx.author.id}>: Your timezone is **{zone}**')
    #     else:
    #         zone = db.get_timezone(user.id)
    #         if zone is None:
    #             await send_embed(ctx, f'<@{ctx.author.id}>: {user.name} doesnt have a timezone set')
    #             return
    #         else:
    #             await send_embed(ctx, f'<@{ctx.author.id}>: {user.name}\'s timezone is **{zone}**')

    @tz.command(name='help', brief='bot usage help')
    async def help(self, ctx):
        description = """
            `,tz [@user|nickname|username|ID]` -> get the time of a user. If user option is empty then you get your own time.

            `,tz set <timezone>` -> set your own timezone.
                Examples:
                    ,tz set Europe/Vienna
                    ,tz set vienna

            you can see supported timezones here:
                <https://gist.github.com/Soheab/3bec6dd6c1e90962ef46b8545823820d>
        """

        embed = discord.Embed(
            title="Help", description=description, color=0x7F00FF
        )

        await send_embed(ctx, "", embed)

    # todo implement
    @tz.command(name='diff', brief='Time difference between 2 users')
    async def diff(self, ctx, user1: str, user2: str):
        return

async def setup(bot):
    await bot.add_cog(tzCog(bot))
