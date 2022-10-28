from code import interact
from pydoc import describe
from unicodedata import decimal
import discord as discord
from discord import app_commands
from discord.ext import commands, tasks
from discord.utils import get
import humanfriendly, random, math, json, asyncio, datetime
from datetime import datetime, timedelta


class moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    





        

    @app_commands.command(name="help", description="Command list & information about me!")
    async def help(self, interaction: discord.Interaction):
        e = discord.Embed(title="Help", description="To Be Finished...", color=discord.Color.blue())
        await interaction.response.send_message(embed=e)

    @commands.Cog.listener()
    async def on_ready(self):
        print("Logged into the bot successfully!")
    


    @commands.is_owner()
    @commands.command()
    async def status(self, ctx):
        await ctx.message.add_reaction("✅")
        self.change_status.start()



async def setup(bot):
    await bot.add_cog(moderation(bot))