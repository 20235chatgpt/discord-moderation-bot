import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

warnings_db = {}

def get_prefix(bot, message):
    if message.author.guild_permissions.administrator:
        return ["!", ""]
    return ["!"]

bot = commands.Bot(command_prefix=get_prefix, intents=intents)

async def is_admin(ctx):
    return ctx.author.guild_permissions.administrator

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if bot.user in message.mentions:
        msg = message.content.lower()

        if "help" in msg:
            await message.channel.send("🛡 Available commands: !kick !ban !warn !warnings")

        elif "rules" in msg:
            await message.channel.send("📜 Please follow server rules and respect others.")

        else:
            await message.channel.send("🤖 I'm a moderation bot. Use !help for commands.")

    await bot.process_commands(message)

@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user}")

@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="No reason provided"):
    await member.kick(reason=reason)
    await ctx.send(f"👢 {member} was kicked.\nReason: {reason}")

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="No reason provided"):
    await member.ban(reason=reason)
    await ctx.send(f"🔨 {member} was banned.\nReason: {reason}")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    await ctx.channel.purge(limit=amount+1)
    await ctx.send(f"🧹 Cleared {amount} messages", delete_after=5)

@bot.command()
@commands.has_permissions(manage_messages=True)
async def warn(ctx, member: discord.Member, *, reason="No reason provided"):
    user_id = str(member.id)

    if user_id not in warnings_db:
        warnings_db[user_id] = []

    warnings_db[user_id].append(reason)
    warn_count = len(warnings_db[user_id])

    await ctx.send(f"⚠️ {member} warned.\nReason: {reason}\nTotal warnings: {warn_count}")

    # Auto punishment
    if warn_count == 3:
        await member.timeout(discord.utils.utcnow() + discord.timedelta(minutes=10))
        await ctx.send(f"⏳ {member} has been timed out for 10 minutes (3 warnings)")

    elif warn_count == 5:
        await member.ban(reason="Reached 5 warnings")
        await ctx.send(f"🔨 {member} has been banned (5 warnings)")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def warnings(ctx, member: discord.Member):
    user_id = str(member.id)

    if user_id not in warnings_db or len(warnings_db[user_id]) == 0:
        await ctx.send(f"✅ {member} has no warnings.")
        return

    warn_list = warnings_db[user_id]
    msg = "\n".join([f"{i+1}. {w}" for i, w in enumerate(warn_list)])

    await ctx.send(f"⚠️ Warnings for {member}:\n{msg}")

bot.run(os.getenv("DISCORD_TOKEN"))
