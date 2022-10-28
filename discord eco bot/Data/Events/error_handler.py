from code import interact
from pydoc import describe
from unicodedata import decimal
import discord as discord
from discord import app_commands
from discord.ext import commands, tasks
from discord.utils import get
import humanfriendly, random, math, json, asyncio, datetime
from datetime import datetime, timedelta


class error_handler(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_command_error(self, ctx, error):

		if isinstance(error, commands.CommandNotFound):
			if ctx.channel.id == 815763224627773453:
				return
			e = discord.Embed(title="Error", description=":x: Command not found.", color=discord.Color.blue())
			await ctx.send(embed=e)
			return

		if isinstance(error, commands.BotMissingPermissions):
			missing = [perm.replace('_', ' ').replace('guild', 'server').title() for perm in error.missing_perms]
			if len(missing) > 2:
				fmt = '{}, and {}'.format("**, **".join(missing[:-1]), missing[-1])
			else:
				fmt = ' and '.join(missing)
			_message = discord.Embed(title="Error", description=f':x: I need the **{fmt}** permission(s) to run this command.', color=discord.Color.blue())
			await ctx.send(embed=_message)
			return

		if isinstance(error, commands.DisabledCommand):
			await ctx.send(embed=discord.Embed(title="Error", description=f':x: This command has been disabled.', color=discord.Color.blue()))
			return
		if isinstance(error, commands.CommandOnCooldown):
			await ctx.send(embed=discord.Embed(title="Error", description=f":x: This command is on cooldown, please retry in **{datetime.timedelta(seconds=(math.ceil(error.retry_after)))}**.", color=discord.Color.blue()))

			return

		if isinstance(error, commands.MissingPermissions):
			missing = [perm.replace('_', ' ').replace('guild', 'server').title() for perm in error.missing_perms]
			if len(missing) > 2:
				fmt = '{}, and {}'.format("**, **".join(missing[:-1]), missing[-1])
			else:
				fmt = ' and '.join(missing)
			_message = discord.Embed(title="Error", description=f':x: You need the **{fmt}** permission(s) to run this command.', color=discord.Color.blue())
			await ctx.send(embed=_message)

		if isinstance(error, commands.UserInputError):
			await ctx.send(embed=discord.Embed(title="Error", description=":x: Invalid input!", color=discord.Color.blue()), delete_after=3)
			await ctx.message.delete()
			return

		if isinstance(error, commands.NoPrivateMessage):
			try:
				await ctx.author.send(embed=discord.Embed(title="Error", description=':x: This command cannot be used in direct messages.', color=discord.Color.blue()))
			except discord.Forbidden:
				pass
			return

		if isinstance(error, commands.CheckFailure):
			await ctx.send(embed=discord.Embed(title="Error", description=":x: You cannot use this command in this channel.", color=discord.Color.blue()))
			return



		else:
			raise error

async def setup(bot):
	await bot.add_cog(error_handler(bot))