import discord as discord
from discord.ext import commands, tasks
import os, math, datetime, asyncio, random, logging

def prefixes(client, message):

	prefix = ["z!", "z"]
	return commands.when_mentioned_or(*prefix)(bot, message)

intents = discord.Intents.default()
intents.members = True
intents.presences = True
intents.message_content = True

bot = commands.Bot(
	command_prefix = prefixes,
	case_insensitive=True,
	strip_after_prefix=True,
	intents = intents
)

async def load():
	for filename in os.listdir('Data/Commands/'):
		if filename.endswith('.py'):
			try:
				await bot.load_extension(f'Data.Commands.{filename[:-3]}')
			except Exception as e:
				print(e)

	for filename in os.listdir('Data/Events/'):
		if filename.endswith('.py'):
			try:
				await bot.load_extension(f'Data.Events.{filename[:-3]}')
			except Exception as e:
				print(e)

discord.utils.setup_logging(level=logging.INFO, root=False)


async def main():
	async with bot:
		bot.loop.create_task(load())
		await bot.start("MTAzMTMwNjUwNDk5MDYyOTk3OA.Gq7l95.UVppOBLmRKh96leOGvHuI3FHSyLp3-_IqsifDE")

asyncio.run(main())