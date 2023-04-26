import discord
from discord.ext import commands

#################
## Discord Bot ##
#################
intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix=".", intents=intents)

@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.dnd , activity=discord.Activity(type=discord.ActivityType.watching, name="the maintenance."))
    print("Logged in as {0.user}".format(client))

@client.event
async def on_guild_join(guild):
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            message = [
                f"Thank you for adding me to your server!\n"
                f"If you are server owner, you can add your staff roles to the manager group using `.setmanager <ping the role here>`."
                f" This will allow your moderators to use the moderation commands of the bot."
                f" Note that the Administrator Permission does not give automatic access to the manager group."
                f"\nYou can use `.commands` to see a list of all commands and `.info` to get more information about the bot. If you have any questions please feel free to contact me."
                f"\n\nTHE BOT IS CURRENTLY IN MAINTENANCE"
            ] 
            await channel.send(''.join(message))
        break

@client.event
async def on_message(ctx):
    if ctx.content.startswith("."):
        await ctx.channel.send("The bot is currently in maintenance. It will be back as soon as possible.")

client.run("NjU1NDQ2NTU0NTA0NTkzNDU4.GaQnB3.TP20URYe0V7fmZta5S07R1elaCa20bpABO_Ymw")