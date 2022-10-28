from code import interact
from dis import disco
from pydoc import describe
from unicodedata import decimal
import discord as discord
from discord import app_commands
from discord.ext import commands, tasks
from discord.utils import get
import humanfriendly, random, math, json, asyncio, datetime, aiosqlite, time
from datetime import datetime, timedelta
from typing import Literal

from numpy import isin

class eco(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    



    async def open_account(self, member: discord.Member):
        db = await aiosqlite.connect("money.db")
        cursor = await db.cursor()
        await cursor.execute(f"SELECT * from money WHERE member_id = {member.id}")
        result = await cursor.fetchone()

        if result:
            return
        if not result:
            await cursor.execute(f"INSERT INTO money(member_id, wallet, bank) VALUES(?, ?, ?)", (member.id, 100, 0))

        
        await db.commit()
        await cursor.close()
        await db.close()

    async def open_streak_account(self, member: discord.Member):
        db = await aiosqlite.connect("streaks.db")
        cursor = await db.cursor()
        await cursor.execute(f"SELECT * from streaks WHERE member_id = {member.id}")
        result = await cursor.fetchone()

        if result:
            return
        if not result:
            await cursor.execute(f"INSERT INTO streaks(member_id, streak, time, work_cooldown) VALUES(?, ?, ?, ?)", (member.id, 0, 0, 0))

        
        await db.commit()
        await cursor.close()
        await db.close()
    

    #@commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        await self.open_account(member=member)
        await self.open_streak_account(member=member)
    


    @commands.is_owner()
    @commands.command()
    async def eval(self, ctx, *, msg):
        a = eval(msg)
        await ctx.send(a)

    @commands.is_owner()
    @commands.command()
    async def open_ac(self, ctx, member: discord.Member=None):
        if member == None:
            member = ctx.author
        await self.open_account(member)
        await self.open_streak_account(member)
        await ctx.send("Account opened.")

    @commands.command()
    @commands.is_owner()
    async def sync(self, ctx):
        guild = self.bot.get_guild(815763223856021564)
        await self.bot.tree.sync(guild=guild)
        await ctx.send("succesfully synced!")
    

    
    @app_commands.command(name="leaderboard", description="Check the coin leaderboard!")
    @app_commands.guilds(discord.Object(id=815763223856021564))
    async def leaderboard(self, interaction: discord.Interaction, member: discord.Member = None):

        db = await aiosqlite.connect("money.db")
        cursor = await db.cursor()
        users = await cursor.execute("SELECT member_id, wallet + bank FROM money ORDER BY wallet + bank DESC")
        users = await users.fetchall()


        await cursor.close()
        await db.close()
        
        data = ""


        for member in users:
            
            
            member_name = self.bot.get_user(member[0])
            member_net = member[1]




            if member[0] == users[0][0]:
                data += f"\n**1  🥇 {member_name} - {member_net}** <:zcoin:837102743280812073>"
            if member[0] == users[1][0]:
                data += f"\n**2  🥈 {member_name} - {member_net}** <:zcoin:837102743280812073>"
            if member[0] == users[2][0]:
                data += f"\n**3  🥉 {member_name} - {member_net}** <:zcoin:837102743280812073>"

        e = discord.Embed(title = f"Z-Coin Leaderboard", description=data, color=discord.Color.blue())
        await interaction.response.send_message(embed=e)
            
    @app_commands.command(name="deposit", description="Deposit money into your bank.")
    @app_commands.guilds(discord.Object(id=815763223856021564))
    async def deposit(self, interaction: discord.Interaction, amount: int):

        db = await aiosqlite.connect("money.db")
        cursor = await db.cursor()
        await cursor.execute(f"SELECT * from money WHERE member_id = {interaction.user.id}")
        result = await cursor.fetchone()



        if result[1] < amount:
            e = discord.Embed(title="Deposit unsuccessful due to insufficient funds.", color=discord.Color.blue())
            await interaction.response.send_message(embed=e, ephemeral=True)
            return

        wallet = result[1] - amount
        bank = result[2] + amount
        
        await cursor.execute(f"UPDATE money SET wallet = {wallet} WHERE member_id = {interaction.user.id}")
        await cursor.execute(f"UPDATE money SET bank = {bank} WHERE member_id = {interaction.user.id}")

        await db.commit()
        await cursor.close()
        await db.close()

        e = discord.Embed(title="Deposit Successful!", description=f"**{amount}** <:zcoin:837102743280812073> has successfully been deposited into your bank!\nYou currently have **{wallet}** <:zcoin:837102743280812073> in your wallet, and **{bank}** <:zcoin:837102743280812073> in your bank!", color=discord.Color.blue())
        await interaction.response.send_message(embed=e)

    @app_commands.command(name="withdraw", description="Withdraw money into your wallet.")
    @app_commands.guilds(discord.Object(id=815763223856021564))
    async def withdraw(self, interaction: discord.Interaction, amount: int):

        db = await aiosqlite.connect("money.db")
        cursor = await db.cursor()
        await cursor.execute(f"SELECT * from money WHERE member_id = {interaction.user.id}")
        result = await cursor.fetchone()



        if result[2] < amount:
            e = discord.Embed(title="Withdrawal unsuccessful due to insufficient funds.", color=discord.Color.blue())
            await interaction.response.send_message(embed=e, ephemeral=True)
            return

        wallet = result[1] + amount
        bank = result[2] - amount
        
        await cursor.execute(f"UPDATE money SET wallet = {wallet} WHERE member_id = {interaction.user.id}")
        await cursor.execute(f"UPDATE money SET bank = {bank} WHERE member_id = {interaction.user.id}")

        await db.commit()
        await cursor.close()
        await db.close()

        e = discord.Embed(title="Withdrawal Successful!", description=f"**{amount}** <:zcoin:837102743280812073> has successfully been deposited into your bank!\nYou currently have **{wallet}** <:zcoin:837102743280812073> in your wallet, and **{bank}** <:zcoin:837102743280812073> in your bank!", color=discord.Color.blue())
        await interaction.response.send_message(embed=e)



    @app_commands.command(name="update_balance", description="Update a members balance!")
    @app_commands.guilds(discord.Object(id=815763223856021564))
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(opts="Set, add, or remove money from a balance.", wb="Wallet or Bank?")
    async def update_wallet(self, interaction: discord.Interaction, member: discord.Member, opts: Literal["Set", "Add", "Remove"], wb: Literal["Wallet", "Bank"], amount: int):



        db = await aiosqlite.connect("money.db")
        cursor = await db.cursor()

        await cursor.execute(f"SELECT * from money WHERE member_id = {member.id}")
        result = await cursor.fetchone()
        wallet = result[1]
        bank = result[2]

        e = discord.Embed(title=f"Successfully {opts} to {member.name}'s {wb}!", color=discord.Color.blue())

        if opts == "Set" and wb == "Wallet":
            await cursor.execute(f"UPDATE money SET wallet = {amount} WHERE member_id = {member.id}")
        
        if opts == "Set" and wb == "Bank":
            await cursor.execute(f"UPDATE money SET bank = {amount} WHERE member_id = {member.id}")
        
        if opts == "Add" and wb == "Wallet":
            await cursor.execute(f"UPDATE money SET wallet = {amount + wallet} WHERE member_id = {member.id}")

        if opts == "Add" and wb == "Bank":
            await cursor.execute(f"UPDATE money SET bank = {amount + bank} WHERE member_id = {member.id}")

        if opts == "Remove" and wb == "Wallet":
            await cursor.execute(f"UPDATE money SET wallet = {wallet - amount} WHERE member_id = {member.id}")

        if opts == "Remove" and wb == "Bank":
            await cursor.execute(f"UPDATE money SET bank = {bank - amount} WHERE member_id = {member.id}")

        

        await db.commit()
        await cursor.close()
        await db.close()

        await interaction.response.send_message(embed=e)
    



    @app_commands.command(name="daily", description="Claim your daily amount of Z-Coins!")
    @app_commands.guilds(discord.Object(id=815763223856021564))
    async def daily(self, interaction: discord.Interaction):

        await self.open_streak_account(member=interaction.user)

        money_db = await aiosqlite.connect("money.db")
        money_cursor = await money_db.cursor()

        streaks_db = await aiosqlite.connect("streaks.db")
        streaks_cursor = await streaks_db.cursor()

        await money_cursor.execute(f"SELECT * from money WHERE member_id = {interaction.user.id}")
        money_result = await money_cursor.fetchone()
        current_money = money_result[1]

        await streaks_cursor.execute(f"SELECT * from streaks WHERE member_id = {interaction.user.id}")
        streaks_result = await streaks_cursor.fetchone()

        current_streak = streaks_result[1]
        last_streak_time = streaks_result[2]

        current_time = int(time.time())

        if current_time - last_streak_time < 86400:
            e = discord.Embed(title=f"You have already collected today's Daily!", description=f"Come back **<t:{last_streak_time + 86400}:R>**!", color=discord.Color.blue())
            await interaction.response.send_message(embed=e, ephemeral=True)
            return

        if current_time - last_streak_time > 172800:
            current_streak = 0

        if current_streak + 1 == 0:
            reward = random.randint(75, 125)
        if current_streak + 1 > 0:
            reward = random.randint(75+(current_streak*5), 125+(current_streak*5))
            if reward > 500:
                reward = 500

        if current_time - last_streak_time > 172800:
            current_streak = 1
            current_money += reward
            
            e = discord.Embed(title="Daily Claimed!", description=f"You have claimed **{reward}** <:zcoin:837102743280812073>!\nCome back in **<t:{current_time + 86400}:R>** to continue your **1** day streak!", color=discord.Color.blue())
            await interaction.response.send_message(embed=e)

        if current_time - last_streak_time < 172800 and current_time - last_streak_time > 86400:
            current_streak += 1
            current_money += reward
            e = discord.Embed(title="Daily Claimed!", description=f"You have claimed **{reward}** <:zcoin:837102743280812073>!\nCome back in **<t:{current_time + 86400}:R>** to continue your **{current_streak}** day streak!", color=discord.Color.blue())
            await interaction.response.send_message(embed=e)
        
        await money_cursor.execute(f"UPDATE money SET wallet = {current_money} WHERE member_id = {interaction.user.id}")
        await streaks_cursor.execute(f"UPDATE streaks SET streak = {current_streak} WHERE member_id = {interaction.user.id}")
        await streaks_cursor.execute(f"UPDATE streaks SET time = {current_time} WHERE member_id = {interaction.user.id}")

        await money_db.commit()
        await streaks_db.commit()

        await money_cursor.close()
        await money_db.close()
        
        await streaks_cursor.close()
        await streaks_db.close()

        

    @app_commands.command(name="balance", description="Check a member's balance!")
    @app_commands.guilds(discord.Object(id=815763223856021564))
    async def balance(self, interaction: discord.Interaction, member: discord.Member = None):
        if member == None:
            member = interaction.user
        
        await self.open_account(member=member)
        await self.open_streak_account(member=member)

        money_db = await aiosqlite.connect("money.db")
        money_cursor = await money_db.cursor()

        streaks_db = await aiosqlite.connect("streaks.db")
        streaks_cursor = await streaks_db.cursor()



        await money_cursor.execute(f"SELECT * from money WHERE member_id = {member.id}")
        money_result = await money_cursor.fetchone()

        await streaks_cursor.execute(f"SELECT * from streaks WHERE member_id = {member.id}")
        streaks_result = await streaks_cursor.fetchone()

        e = discord.Embed(title=f"{member.name}'s Balance", description=f":coin: Wallet: **{money_result[1]} <:zcoin:837102743280812073>**\n:bank: Bank: **{money_result[2]} <:zcoin:837102743280812073>**\n\nDaily Streak: **{streaks_result[1]}**\nNext Daily: **<t:{streaks_result[2] + 86400}:R>**", color=discord.Color.blue())


        await interaction.response.send_message(embed=e)

        await money_cursor.close()
        await money_db.close()
        await streaks_cursor.close()
        await streaks_db.close()

    @app_commands.command(name="work", description="Complete a Job to earn Z-Coins!")
    @app_commands.guilds(discord.Object(id=815763223856021564))
    async def work(self, interaction: discord.Interaction):
        
        money_db = await aiosqlite.connect("money.db")
        money_cursor = await money_db.cursor()

        streaks_db = await aiosqlite.connect("streaks.db")
        streaks_cursor = await streaks_db.cursor()

        await money_cursor.execute(f"SELECT * from money WHERE member_id = {interaction.user.id}")
        money_result = await money_cursor.fetchone()
        current_money = money_result[1]

        await streaks_cursor.execute(f"SELECT * from streaks WHERE member_id = {interaction.user.id}")
        streaks_result = await streaks_cursor.fetchone()


        if int(time.time()) - streaks_result[3] < 3600:
            e = discord.Embed(title="You are not able to work!", description=f"Come back and try **<t:{streaks_result[3] + 3600}:R>**!", color = discord.Color.yellow())
            await interaction.response.send_message(embed=e, ephemeral=True)
            return

        opts = random.choice(["n", "n", "n", "n", "n", "n", "n", "r"])

        await streaks_cursor.execute(f"UPDATE streaks SET work_cooldown = {int(time.time())} WHERE member_id = {interaction.user.id}")

        await streaks_db.commit()
        await streaks_cursor.close()
        await streaks_db.close()


        if opts == "r":
            num1 = random.randint(100, 999)
            num2 = random.randint(100, 999)
            num3 = random.randint(100, 999)

            def check(message):
                return message.author == interaction.user

            reward = random.randint(350, 800)

            e = discord.Embed(title="YOU FOUND A RARE JOB!", description=f"{interaction.user.display_name}, you have been offered a rare job opportunity! To obtain your reward of **{reward}**  <:zcoin:837102743280812073>, solve the following equation to help get the Arcade's power back up!\n\n```{num1}‏‏‎ ‎ +‏‏‎ ‎ {num2}‏‏‎ ‎ + ‏‏‎ ‎{num3}```", color=discord.Color.blue())
            e.set_footer(text="Reply to this message with the answer to complete your Job!")
            e.set_thumbnail(url="https://cdn.discordapp.com/attachments/903510018870104074/1032116231748194314/IMG_8300.gif")
            await interaction.response.send_message(embed=e)

            try:
                message = await self.bot.wait_for("message", timeout=45, check=check)
            except asyncio.TimeoutError:
                answer = "wrong"
                await interaction.edit_original_response(content="You have taken to long to reply.")
                return

            
            if message.content == str(num1 + num2 + num3):
                answer = "right"
            if message.content != str(num1 + num2 + num3):
                answer = "wrong"



            if answer == "wrong":
                e = discord.Embed(title="Rare Job Failed!", description=f"The correct answer was **{num1 + num2 + num3}**!", color=discord.Color.red())
                await interaction.edit_original_response(embed=e)

                await money_cursor.close()
                await money_db.close()


                return
            
            if answer == "right":
                e = discord.Embed(title="Job Successful!", description=f"Yay, you have completed the job, and have been rewarded with **{reward}** <:zcoin:837102743280812073>!", color=discord.Color.blue())
                await interaction.edit_original_response(embed=e)

                await money_cursor.execute(f"UPDATE money SET wallet = {current_money + reward} WHERE member_id = {interaction.user.id}")
                await money_db.commit()

                await money_cursor.close()
                await money_db.close()
                return

        if opts == "n":
            num = random.randint(10, 99)
            num2 = random.randint(10, 99)

            def check(message):
                return message.author == interaction.user

            reward = random.randint(50, 150)

            e = discord.Embed(title="Job Started!", description=f"{interaction.user.display_name}, you just started cleaning up the arcade! Solve this additon problem to get an extra tip of **{reward}** <:zcoin:837102743280812073>!\n\n```{num} ‏‏‎ ‎+ ‏‏‎ ‎{num2}```", color=discord.Color.blue())
            e.set_footer(text="Reply to this message with the answer to complete your Job!")
            await interaction.response.send_message(embed=e)

            try:
                message = await self.bot.wait_for("message", timeout=45, check=check)
            except asyncio.TimeoutError:
                answer = "wrong"
                await interaction.edit_original_response("You have taken to long to reply.")
                return

            if message.content == str(num + num2):
                answer = "right"
            if message.content != str(num + num2):
                answer = "wrong"


            if answer == "wrong":
                e = discord.Embed(title="Job Failed!", description=f"The correct answer was **{num + num2}**!", color=discord.Color.red())
                await interaction.edit_original_response(embed=e)

                await money_cursor.close()
                await money_db.close()


                return
            
            if answer == "right":
                e = discord.Embed(title="Job Successful!", description=f"Yay, you have completed the job, and have been rewarded with **{reward}** <:zcoin:837102743280812073>!", color=discord.Color.blue())
                await interaction.edit_original_response(embed=e)

                await money_cursor.execute(f"UPDATE money SET wallet = {current_money + reward} WHERE member_id = {interaction.user.id}")
                await money_db.commit()

                await money_cursor.close()
                await money_db.close()
                return


    @app_commands.command(name="dice", description="Roll two dice and win it big!")
    @app_commands.guilds(discord.Object(id=815763223856021564))
    @app_commands.checks.cooldown(1, 12)
    async def dice(self, interaction: discord.Interaction, amount: int):
        if amount > 300:
            e = discord.Embed(title=f"The most you can play for is 300 Z-Coins.", color=discord.Color.red())
            await interaction.response.send_message(embed=e, ephemeral=True)
            return
        
        if amount < 25:
            e = discord.Embed(title=f"The least you can play for is 25 Z-Coins.", color=discord.Color.red())
            await interaction.response.send_message(embed=e, ephemeral=True)
            return
        
        db = await aiosqlite.connect("money.db")
        cursor = await db.cursor()

        await cursor.execute(f"SELECT * from money WHERE member_id = {interaction.user.id}")
        result = await cursor.fetchone()
        wallet = result[1]

        if amount > wallet:
            e = discord.Embed(title=f"Game canceled due to insufficient funds!", color=discord.Color.red())
            await interaction.response.send_message(embed=e, ephemeral=True)
            return

        player1 = random.randint(1, 6)
        player2 = random.randint(1, 6)

        bot1 = random.randint(1, 6)
        bot2 = random.randint(1, 6)

        await cursor.execute(f"UPDATE money SET wallet = {wallet - amount} WHERE member_id = {interaction.user.id}")
        await db.commit()


        await interaction.response.send_message(f"🎲 {interaction.user.display_name} puts up **{amount}** <:zcoin:837102743280812073>, and rolls their die...")
        await asyncio.sleep(3)
        await interaction.edit_original_response(content=f"🎲 {interaction.user.display_name} puts up **{amount}** <:zcoin:837102743280812073>, and rolls their die...\n🎲 {interaction.user.display_name} rolls a **{player1}** and **{player2}**...")
        await asyncio.sleep(3)
        await interaction.edit_original_response(content=f"🎲 {interaction.user.display_name} puts up **{amount}** <:zcoin:837102743280812073>, and rolls their die...\n🎲 {interaction.user.display_name} rolls a **{player1}** and **{player2}**...\n🎲 {interaction.user.display_name}, your opponent rolls their die, and rolls a **{bot1}** and **{bot2}**...")
        await asyncio.sleep(3)
        
        await cursor.execute(f"SELECT * from money WHERE member_id = {interaction.user.id}")
        result = await cursor.fetchone()
        wallet = result[1]

        if player1 == 6 and player2 == 6:
            await interaction.edit_original_response(content=f"🎲 {interaction.user.display_name} puts up **{amount}** <:zcoin:837102743280812073>, and rolls their die...\n🎲 {interaction.user.display_name} rolls a **{player1}** and **{player2}**...\n🎲 {interaction.user.display_name}, your opponent rolls their die, and rolls a **{bot1}** and **{bot2}**...\n😲 Congratulations, {interaction.user.display_name}, you won your bet and rolled **A SNAKE EYE** and walked away with an extra **{amount*3}** <:zcoin:837102743280812073>!")
            await cursor.execute(f"UPDATE money SET wallet = {wallet + amount*4} WHERE member_id = {interaction.user.id}")
            await db.commit()
            await cursor.close()
            await db.close()
            return


        if player1 + player2 > bot1 + bot2:
            await interaction.edit_original_response(content=f"🎲 {interaction.user.display_name} puts up **{amount}** <:zcoin:837102743280812073>, and rolls their die...\n🎲 {interaction.user.display_name} rolls a **{player1}** and **{player2}**...\n🎲 {interaction.user.display_name}, your opponent rolls their die, and rolls a **{bot1}** and **{bot2}**...\n🎲 {interaction.user.display_name}, you won your bet and walked away with an extra **{amount}** <:zcoin:837102743280812073>!")
            await cursor.execute(f"UPDATE money SET wallet = {wallet + amount + amount} WHERE member_id = {interaction.user.id}")
            await db.commit()
            await cursor.close()
            await db.close()
        
        if player1 + player2 < bot1 + bot2:
            await interaction.edit_original_response(content=f"🎲 {interaction.user.display_name} puts up **{amount}** <:zcoin:837102743280812073>, and rolls their die...\n🎲 {interaction.user.display_name} rolls a **{player1}** and **{player2}**...\n🎲 {interaction.user.display_name}, your opponent rolls their die, and rolls a **{bot1}** and **{bot2}**...\n🎲 {interaction.user.display_name}, you lost your bet of **{amount}** <:zcoin:837102743280812073>!")
            
            await db.commit()
            await cursor.close()
            await db.close()
        
        if player1 + player2 == bot1 + bot2:
            await interaction.edit_original_response(content=f"🎲 {interaction.user.display_name} puts up **{amount}** <:zcoin:837102743280812073>, and rolls their die...\n🎲 {interaction.user.display_name} rolls a **{player1}** and **{player2}**...\n🎲 {interaction.user.display_name}, your opponent rolls their die, and rolls a **{bot1}** and **{bot2}**...\n🎲 {interaction.user.display_name}, you drew with your opponent and didn't lose your **{amount}** <:zcoin:837102743280812073>!")
            await cursor.execute(f"UPDATE money SET wallet = {wallet + amount} WHERE member_id = {interaction.user.id}")
            await cursor.close()
            await db.close()
            


    async def cog_app_command_error(self, interaction: discord.Interaction, error: app_commands.CommandOnCooldown):
        e = discord.Embed(title=f"{str(error)}.", color=discord.Color.red())
        try:
            await interaction.response.send_message(embed=e, ephemeral=True)
        except:
            await interaction.edit_original_response(content=None, embed=e)


    @app_commands.command(name="guess", description="Guess a random number between 1 and 100!")
    @app_commands.guilds(discord.Object(id=815763223856021564))
    @app_commands.checks.cooldown(1, 12)
    async def num(self, interaction: discord.Interaction, amount: int):
        if amount > 300:
            e = discord.Embed(title=f"The most you can play for is 300 Z-Coins.", color=discord.Color.red())
            await interaction.response.send_message(embed=e, ephemeral=True)
            return
        
        if amount < 25:
            e = discord.Embed(title=f"The least you can play for is 25 Z-Coins.", color=discord.Color.red())
            await interaction.response.send_message(embed=e, ephemeral=True)
            return
        
        db = await aiosqlite.connect("money.db")
        cursor = await db.cursor()

        await cursor.execute(f"SELECT * from money WHERE member_id = {interaction.user.id}")
        result = await cursor.fetchone()
        wallet = result[1]

        if amount > wallet:
            e = discord.Embed(title=f"Game canceled due to insufficient funds!", color=discord.Color.red())
            await interaction.response.send_message(embed=e, ephemeral=True)
            return

        await cursor.execute(f"UPDATE money SET wallet = {wallet - amount} WHERE member_id = {interaction.user.id}")
        await db.commit()

        def check(message):
            return message.author == interaction.user

        msg = f"🤔 {interaction.user.display_name} puts-up {amount} <:zcoin:837102743280812073>, and starts the mystery machine..."

        num = str(random.randint(1, 100))
        print(num)

        correct = False

        for x in range(1, 7):
            if x != 1:
                try:
                    message = await self.bot.wait_for("message", timeout=45, check=check)
                except asyncio.TimeoutError:
                    await interaction.edit_original_response(content="You have taken too long to reply. Game canceled.")
                    return
                
                try:
                    if int(message.content) > 100 or int(message.content) < 0:
                        await interaction.edit_original_response(content="You have entered an invalid number.")
                        return
                except:
                    if str(message.content):
                        await interaction.edit_original_response(content="You may only enter a number.")
                        return 


                    
            if x == 1:
                await interaction.response.send_message(msg)
                await asyncio.sleep(2)
                msg += f"\n🤔 {interaction.user.display_name}, the mystery machine is ready! You have **5 attempts** to guess the number **between 1 and 100**... type your answer!\n*Attempt 1/5!*\n"
                await interaction.edit_original_response(content=msg)
            
            if x == 2:
                if message.content > num:
                    msg = f"🤔 {interaction.user.display_name}, the number you are looking for **is less than {message.content}**!\n*Attempt 2/5!*\n"
                    await interaction.edit_original_response(content=msg)

                if message.content < num:
                    msg = f"🤔 {interaction.user.display_name}, the number you are looking for **is greater than {message.content}**!\n*Attempt 2/5!*\n"
                    await interaction.edit_original_response(content=msg)

                if message.content == num:
                    correct = True
                    multi = 10
                    lvl = 1
                    break

            if x == 3:
                if message.content > num:
                    msg = f"🤔 {interaction.user.display_name}, the number you are looking for **is less than {message.content}**!\n*Attempt 3/5!*\n"
                    await interaction.edit_original_response(content=msg)

                if message.content < num:
                    msg = f"🤔 {interaction.user.display_name}, the number you are looking for **is greater than {message.content}**!\n*Attempt 3/5!*\n"
                    await interaction.edit_original_response(content=msg)

                if message.content == num:
                    correct = True
                    multi = 5
                    lvl = 2
                    break

            if x == 4:
                if message.content > num:
                    msg = f"🤔 {interaction.user.display_name}, the number you are looking for **is less than {message.content}**!\n*Attempt 4/5!*\n"
                    await interaction.edit_original_response(content=msg)

                if message.content < num:
                    msg = f"🤔 {interaction.user.display_name}, the number you are looking for **is greater than {message.content}**!\n*Attempt 4/5!*\n"
                    await interaction.edit_original_response(content=msg)

                if message.content == num:
                    correct = True
                    multi = 2
                    lvl = 3
                    break

            if x == 5:
                if message.content > num:
                    msg = f"🤔 {interaction.user.display_name}, the number you are looking for **is less than {message.content}**!\n*Attempt 5/5!*\n"
                    await interaction.edit_original_response(content=msg)

                if message.content < num:
                    msg = f"🤔 {interaction.user.display_name}, the number you are looking for **is greater than {message.content}**!\n*Attempt 5/5!*\n"
                    await interaction.edit_original_response(content=msg)

                if message.content == num:
                    correct = True
                    multi = 1.5
                    lvl = 4
                    break
            
            if x == 6:
                if message.content == num:
                    correct = True
                    multi = 1
                    lvl = 5
                if message.content != num:
                    correct = False

        if correct == True:
            msg = f"❗ Congratulations {interaction.user.display_name}, you have guessed the number **{num}** correctly! You completed it on try **{lvl}**, and won **{amount*multi}** <:zcoin:837102743280812073>!"
            await interaction.edit_original_response(content=msg)
            await cursor.execute(f"UPDATE money SET wallet = {wallet + amount + (amount*multi)} WHERE member_id = {interaction.user.id}")
            await db.commit()
            await cursor.close()
            await db.close()
        
        if correct == False:
            msg = f"🙁 Sorry {interaction.user.display_name}, you have not guessed the number **{num}** correctly! You have lost your bet of **{amount}** <:zcoin:837102743280812073>!"
            await interaction.edit_original_response(content=msg)
            await cursor.close()
            await db.close()


    @app_commands.command(name="duel", description="Duel another member to win Z-Coins!")
    @app_commands.guilds(discord.Object(id=815763223856021564))
    @app_commands.checks.cooldown(1, 12)
    async def duel(self, interaction: discord.Interaction, player: discord.Member, amount: int):

        if player == interaction.user:
            e = discord.Embed(title="You cannot duel yourself.", color=discord.Color.red())
            await interaction.response.send_message(embed=e, ephemeral=True)
            return

        if amount > 300:
            e = discord.Embed(title=f"The most you can play for is 300 Z-Coins.", color=discord.Color.red())
            await interaction.response.send_message(embed=e, ephemeral=True)
            return
        
        if amount < 25:
            e = discord.Embed(title=f"The least you can play for is 25 Z-Coins.", color=discord.Color.red())
            await interaction.response.send_message(embed=e, ephemeral=True)
            return
        
        db = await aiosqlite.connect("money.db")
        cursor = await db.cursor()

        await cursor.execute(f"SELECT * from money WHERE member_id = {interaction.user.id}")
        result = await cursor.fetchone()
        user_wallet = result[1]

        if amount > user_wallet:
            e = discord.Embed(title=f"Game canceled due to insufficient funds!", color=discord.Color.red())
            await interaction.response.send_message(embed=e, ephemeral=True)
            await cursor.close()
            await db.close()
            return
        
        await cursor.execute(f"SELECT * from money where member_id = {player.id}")
        result = await cursor.fetchone()
        player_wallet = result[1]
        
        if amount > player_wallet:
            e = discord.Embed(title=f"Game canceled due to opponent not having sufficient funds!", color=discord.Color.red())
            await interaction.response.send_message(embed=e)
            await cursor.close()
            await db.close()
            return
        
        view = Confirm(player)

        await interaction.response.send_message(f"**{player.mention}**, do you accept this duel from **{interaction.user.display_name}** for **{amount}** <:zcoin:837102743280812073>!", view=view)
        
        await view.wait()

        if view.value == False or view.value == None:
            await interaction.edit_original_response(content=f"{interaction.user.display_name}, {player.display_name} has declined your duel request.", view=None)
            return()
        
        if view.value == True:
            await interaction.edit_original_response(content=f"{interaction.user.display_name}, {player.display_name} has accepted your duel request!", view=None)
        
        await cursor.execute(f"UPDATE money SET wallet = {player_wallet - amount} WHERE member_id = {interaction.user.id}")
        await cursor.execute(f"UPDATE money SET wallet = {user_wallet - amount} WHERE member_id = {interaction.user.id}")

        await db.commit()

        await asyncio.sleep(2.5)

        view = DuelChoose(interaction.user)

        await interaction.edit_original_response(content=f"**{interaction.user.display_name}**, what would you like to attack with?", view=view)

        await view.wait()

        int_auth_opt = view.opt

        view = DuelChoose(player)

        await interaction.edit_original_response(content=f"**{player.display_name}**, what would you like to attack with?", view=view)

        await view.wait()

        player_opt = view.opt

        inter_num = random.randint(1, 100)

        player_num = random.randint(1, 100)

        await interaction.edit_original_response(content="**Get ready to rumble!**", view=None)

        await asyncio.sleep(3)

        msg = ""

        if int_auth_opt == "pizza":
            msg += f"{interaction.user.display_name} pulls out the undercooked, hard as a rock slice of 🍕 and slaps {player.display_name}. They fall back, taking **{inter_num}** damage points!\n"
        if int_auth_opt == "chili":
            msg += f"{interaction.user.display_name} takes out a 🌶️ and eats it whole. They go **BEAST** mode and attack {player.display_name}. They fall flat on their face, taking **{inter_num}** damage points!\n"
        if int_auth_opt == "avocado":
            msg += f"{interaction.user.display_name} rips out an 🥑 and takes the rock hard pit out. They throw it fast ball style  right into the face of {player.display_name}. They fly backwards, taking **{inter_num}** damage points!\n"

        await interaction.edit_original_response(content=msg, view=None)

        if player_opt == "pizza":
            msg += f"{player.display_name} pulls out the undercooked, hard as a rock slice of 🍕 and slaps {interaction.user.display_name}. They fall back, taking **{player_num}** damage points!"
        if player_opt == "chili":
            msg += f"{player.display_name} takes out a 🌶️ and eats it whole. They go **BEAST** mode and attack {interaction.user.display_name}. They fall flat on their face, taking **{player_num}** damage points!"
        if player_opt == "avocado":
            msg += f"{player.display_name} rips out an 🥑 and takes the rock hard pit out. They throw it fast ball style  right into the face of {interaction.user.display_name}. They fly backwards, taking **{player_num}** damage points!"

        await asyncio.sleep(4)

        await interaction.edit_original_response(content=msg)

        await asyncio.sleep(4)

        if inter_num > player_num:
            winner = interaction.user
            winner_wallet = user_wallet
            loser = player
        
        if player_num > inter_num:
            winner = player
            winner_wallet = player_wallet
            loser = interaction.user

        e = discord.Embed(title="We Have a Winner!", description=f"**{winner.display_name}** has won the duel against **{loser.display_name}** and has been awarded with **{amount}** <:zcoin:837102743280812073>!\n\nThanks for playing!", color=discord.Color.green())
        await interaction.channel.send(embed=e)

        db = await aiosqlite.connect("money.db")
        cursor = await db.cursor()

        await cursor.execute(f"UPDATE money SET wallet = {winner_wallet + amount + amount} WHERE member_id = {winner.id}")
        await db.commit()
        await cursor.close()
        await db.close()
        

    @app_commands.command(name="darts", description="Throw darts at a balloon in hopes of winning a prize! Cost: 300 Z-Coins")
    @app_commands.guilds(discord.Object(id=815763223856021564))
    @app_commands.checks.cooldown(1, 12)
    async def darts(self, interaction: discord.Interaction):

        
        db = await aiosqlite.connect("money.db")
        cursor = await db.cursor()

        await cursor.execute(f"SELECT * from money WHERE member_id = {interaction.user.id}")
        result = await cursor.fetchone()
        user_wallet = result[1]

        if 300 > user_wallet:
            e = discord.Embed(title=f"Game canceled due to insufficient funds!", color=discord.Color.red())
            await interaction.response.send_message(embed=e, ephemeral=True)
            await cursor.close()
            await db.close()
            return
        
        await cursor.execute(f"UPDATE money SET wallet = {user_wallet - 300} WHERE member_id = {interaction.user.id}")
        await db.commit()


        
async def setup(bot):
    await bot.add_cog(eco(bot))

        
class DartView(discord.ui.view):
    def __init__(self, message):
        super().__init__(timeout=20)
        self.value = None
    
    @discord.ui.button(label="🎈", style=discord.ButtonStyle.green)
    async def top_left(self, interaction: discord.Interaction):
        miss = random.randint(1, 4)
        if miss == 1:


            

class Confirm(discord.ui.View):
    def __init__(self, challenged):
        super().__init__()
        self.value = None
        self.challenged = challenged
    
    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.challenged:
            await interaction.response.send_message("You cannot use this button.", ephemeral=True)
            return
        await interaction.response.send_message("Game beginning soon.", ephemeral=True)
        self.value = True
        self.stop()
    
    @discord.ui.button(label="Decline", style=discord.ButtonStyle.red)
    async def deny(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.challenged:
            await interaction.response.send_message("You cannot use this button.", ephemeral=True)
            return
        await interaction.response.send_message("Game canceled.", ephemeral=True)
        self.value = False
        self.stop()

class DuelChoose(discord.ui.View):
    def __init__(self, chooser):
        super().__init__()
        self.opt = None
        self.chooser = chooser

    @discord.ui.button(label="Pizza Slice", emoji="🍕", style=discord.ButtonStyle.blurple)
    async def pizza(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.chooser:
            await interaction.response.send_message("You cannot use this button.", ephemeral=True)
            return
        
        await interaction.response.send_message("You have chosen the pizza slice!", ephemeral=True)
        self.opt = "pizza"
        self.stop()

    @discord.ui.button(label="Chili Pepper", emoji="🌶️", style=discord.ButtonStyle.blurple)
    async def chili(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.chooser:
            await interaction.response.send_message("You cannot use this button.", ephemeral=True)
            return
        
        await interaction.response.send_message("You have chosen the chili pepper!", ephemeral=True)
        self.opt = "chili"
        self.stop()

    @discord.ui.button(label="Avocado Pit", emoji="🥑", style=discord.ButtonStyle.blurple)
    async def avocado(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.chooser:
            await interaction.response.send_message("You cannot use this button.", ephemeral=True)
            return
        
        await interaction.response.send_message("You have chosen the avocado pit!", ephemeral=True)
        self.opt = "avocado"
        self.stop()