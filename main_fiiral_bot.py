import discord
from discord.ext import commands

import math
import asyncio
import os
import shutil
import json
import random
import time
import ISS_Info

from cryptography.fernet import Fernet
from datetime import datetime, timedelta

import fiiral_checker_bot
import fiiral_bot_setmanager
import fiiral_bot_delmanager
import fiiral_bot_warn
import fiiral_bot_unwarn
import fiiral_bot_showwarns
import fiiral_bot_autopunish

#####################
###               ###
###  Discord Bot  ###
###               ###
#####################

# Bot settings
intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix=".", intents=intents)
client.remove_command("help")

# Set some global variables
afk_users = {}
server_xp_data = {}
save_xp_data_running = False
empty_argument = "0260056448112582667531450112361548548275"     #This huge string is probably never going to be a username

# Clear AFK Users after restart
with open(f"global/afk/afk.json", "w") as file:
    json.dump({}, file)

#############
# On Action #
#############

# Send a message on ready
@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.online , activity=discord.Activity(type=discord.ActivityType.listening, name=".commands"))
    print("Logged in as {0.user}".format(client))

# Send a message on join
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
            ] 
            await channel.send(''.join(message))
        break

# Nuke all information if the bot is kicked
@client.event
async def on_guild_remove(guild):
    try:
        server_id = guild.id

        if os.path.exists(f"servers/{server_id}"):
            shutil.rmtree(f"servers/{server_id}")
    except:
        return

# XP Manager & AFK Manager
@client.event
async def on_message(ctx):

    # Ignore Bots
    if ctx.author.bot:
       return 

    # AFK Manager
    try:
        if afk_users[str(ctx.author.id)]:
            del afk_users[str(ctx.author.id)]
            with open(f"global/afk/afk.json", "w") as file:
                json.dump(afk_users, file)
                
            try:
                returned_nick = ctx.author.nick.strip("[AFK]").strip()
                await ctx.author.edit(nick=f"{returned_nick}")
                await ctx.channel.send(f"{ctx.author.nick} has returned from AFK.")
            except:
                await ctx.channel.send(f"{ctx.author.name} has returned from AFK.")
    except KeyError:
        pass
    
    user_id = ctx.author.id
    server_id = ctx.guild.id

    # Check if server XP data is already in memory, if not, load it from file, if file does not exist make one
    if server_id not in server_xp_data:
        server_xp_data[server_id] = {}

        if os.path.exists(f"servers/{server_id}/leveling"):
            with open(f"servers/{server_id}/leveling/xp_data.json", "r") as file:
                server_xp_data[server_id] = json.load(file)
        else:
            os.makedirs(f"servers/{server_id}/leveling")
            with open(f"servers/{server_id}/leveling/xp_data.json", "w") as file:
                json.dump({}, file)

    # Check if user XP data is already in memory, if not, create a new entry
    if str(user_id) not in server_xp_data[server_id]:
        server_xp_data[server_id][str(user_id)] = 0

    server_xp_data[server_id][str(user_id)] += 1

    # Levels
    xp_array = [server_xp_data[server_id][str(user_id)], server_xp_data[server_id][str(user_id)] - 1]
    level_array = []

    for y in xp_array:
        a = 0.05
        b = 1
        c = 6
        d = -y
        
        # Use the cubic formula to solve for x
        p = (3*a*c - b**2) / (3*a**2)
        q = (2*b**3 - 9*a*b*c + 27*a**2*d) / (27*a**3)
        delta = (q/2)**2 + (p/3)**3
        
        if delta < 0:
            break # No real solutions exist
        
        u = math.pow(-q/2 + math.sqrt(delta), 1/3)
        v = math.pow(-q/2 - math.sqrt(delta), 1/3)
        
        x = u + v - b/(3*a)
        level_array.append(x)

    if math.floor(level_array[0]) > math.floor(level_array[1]) and math.floor(level_array[0]) % 10 == 0 and math.floor(level_array[0]) != 0:
        await ctx.channel.send(f"You leveled up to level {math.floor(level_array[0])}!")

    global save_xp_data_running
    if save_xp_data_running == False:
        save_xp_data_running = True
        asyncio.create_task(save_xp_data())
    
    await client.process_commands(ctx)

####################
# Utility Commands #
####################

# Info Command
@client.command(aliases=["information"])
async def info(ctx: commands.Context):
    message = [
        f"This bot is a multi-purpose bot created by Fiiral#5870."
        f" It allows for easy moderation, has a leveling system and also include various fun commands."
        f" The bot also has a permission-based system to prohibit abuse of certain commands. `#` denotes Administrators, `♦` denotes Managers."
        f" To see a list of all commands, please type `.commands`."
        f"\n\nPlease contact me if you are experiencing any issues."
    ]

    await ctx.send(''.join(message))

# Help Command
@client.command(aliases=["commands"])
async def help(ctx: commands.Context, help_request="all"):
    
    output = ["I am not sure what you want."]
    if help_request == "all":
        output = [
            f"**Administration**\n",
            f"`#` `.setmanager <role/id>`\n",
            f"`#` `.delmanager <role/id>`\n",
            f"`#` `.serverbackup`\n",
            f"\n**Moderation**\n",
            f"`♦` `.warn <user/id>`\n",
            f"`♦` `.unwarn <user/id> [amount]`\n",
            f"` ` `.showwarns <user/id>`\n",
            f"`♦` `.autopunish <user/id>`\n",
            f"`♦` `.purge [amount] [reason]`\n",
            f"`♦` `.kick <user/id> [reason]`\n",
            f"`♦` `.ban <user/id> [reason]`\n",
            f"`♦` `.softban <user/id> [reason]`\n",
            f"`♦` `.unban <user/id> [reason]`\n",
            f"`♦` `.mute <user/id> [duration in minutes] [reason]`\n",
            f"`♦` `.trust`\n",
            f"\n**Utility**\n",
            f"` ` `.info`\n"
            f"` ` `.commands [command]`\n",
            f"`♦` `.givexp <user/id> [amount]`\n",
            f"` ` `.userinfo <user/id>`\n",
            f"` ` `.serverinfo`\n",
            f"` ` `.afk`\n"
            f"\n**Fun**\n",
            f"` ` `.iss`\n",
            f"` ` `.dice [sides] [rolls] [bonus]`\n",
            f"` ` `.coin`\n",
            f"` ` `.random`\n",
            f"` ` `.color`",
            f"\n\nYou can also use `.commands` to find a certain command to get more information about it."
        ]
    elif help_request == "setmanager" or help_request == "setmoderator" or help_request == "setmod" or help_request == "addmanager" or help_request == "addmoderator" or help_request == "addmod":
        output = [
            f"**.setmanager**\n",
            f"Category: Administration\n"
            f"Permission Level: Administrator `#`\n"
            f"Aliases: `.setmanager` `.setmoderator` `.setmod` `.addmanager` `.addmoderator` `.addmod`\n"
            f"Syntax: `.setmanager <role/id>`\n"
            f"\nAdds a role to the list of Manager Roles."
        ]
    elif help_request == "delmanager" or help_request == "delmoderator" or help_request == "delmod" or help_request == "removemanager" or help_request == "removemoderator" or help_request == "removemod":
        output = [
            f"**.delmanager**\n",
            f"Category: Administration\n"
            f"Permission Level: Administrator `#`\n"
            f"Aliases: `.delmanager` `.delmoderator` `.delmod` `.removemanager` `.removemoderator` `.removemod`\n"
            f"Syntax: `.delmanager <role/id>`\n"
            f"\nRemoves a role to the list of Manager Roles."
        ]
    elif help_request == "serverbackup":
        output = [
            f"**.serverbackup**\n",
            f"Category: Administration\n"
            f"Permission Level: Administrator `#`\n"
            f"Aliases: `.serverbackup`\n"
            f"Syntax: `.serverbackup`\n"
            f"\nSends back a list of all server files and an encrypted key."
        ]
    elif help_request == "warn":
        output = [
            f"**.warn**\n",
            f"Category: Moderation\n"
            f"Permission Level: Manager `♦`\n"
            f"Aliases: `.warn`\n"
            f"Syntax: `.warn <user/id>`\n"
            f"\nAdds a warning to the specified user."
        ]
    elif help_request == "unwarn" or help_request == "removewarn" or help_request == "clearwarn":
        output = [
            f"**.unwarn**\n",
            f"Category: Moderation\n"
            f"Permission Level: Manager `♦`\n"
            f"Aliases: `.unwarn` `.removewarn` `.clearwarn`\n"
            f"Syntax: `.unwarn <user/id> [amount]`\n"
            f"\nRemoves the specified amounts of warnings from the specified user. Default Value: 1"
        ]   
    elif help_request == "showwarns" or help_request == "showwarn":
        output = [
            f"**.showwarns**\n",
            f"Category: Moderation\n"
            f"Permission Level: User ` `\n"
            f"Aliases: `.showwarns` `.showwarn`\n"
            f"Syntax: `.showwarns <user/id>`\n"
            f"\nDisplays the amount of warnings a user has."
        ] 
    elif help_request == "autopunish" or help_request == "punish":
        output = [
            f"**.autopunish**\n",
            f"Category: Moderation\n"
            f"Permission Level: Manager `♦`\n"
            f"Aliases: `.autopunish` `.punish`\n"
            f"Syntax: `.autopunish <user/id>`\n"
            f"\nPunishes a user based on how many warnings they have accumulated."
        ] 
    elif help_request == "purge":
        output = [
            f"**.purge**\n",
            f"Category: Moderation\n"
            f"Permission Level: Manager `♦`\n"
            f"Aliases: `.purge`\n"
            f"Syntax: `.purge [amount] [reason]`\n"
            f"\nDeletes the specified amount of messages."
        ] 
    elif help_request == "kick":
        output = [
            f"**.kick**\n",
            f"Category: Moderation\n"
            f"Permission Level: Manager `♦`\n"
            f"Aliases: `.kick`\n"
            f"Syntax: `.kick <user/id> [reason]`\n"
            f"\nKicks the specified user from the server with the provided reason."
        ] 
    elif help_request == "ban":
        output = [
            f"**.ban**\n",
            f"Category: Moderation\n"
            f"Permission Level: Manager `♦`\n"
            f"Aliases: `.ban`\n"
            f"Syntax: `.ban <user/id> [reason]`\n"
            f"\nBans the specified user from the server with the provided reason. Deletes messages of the past 7 days."
        ] 
    elif help_request == "softban":
        output = [
            f"**.softban**\n",
            f"Category: Moderation\n"
            f"Permission Level: Manager `♦`\n"
            f"Aliases: `.softban`\n"
            f"Syntax: `.softban <user/id> [reason]`\n"
            f"\nBans the specified user from the server with the provided reason. Does not delete any messages."
        ]
    elif help_request == "unban":
        output = [
            f"**.unban**\n",
            f"Category: Moderation\n"
            f"Permission Level: Manager `♦`\n"
            f"Aliases: `.unban`\n"
            f"Syntax: `.unban <user/id> [reason]`\n"
            f"\nUnbans the specified user from the server with the provided reason."
        ]
    elif help_request == "mute" or help_request == "timeout":
        output = [
            f"**.mute**\n",
            f"Category: Moderation\n"
            f"Permission Level: Manager `♦`\n"
            f"Aliases: `.mute` `.timeout`\n"
            f"Syntax: `.mute <user/id> [duration in minutes] [reason]`\n"
            f"\nTimeouts the specified user with the provided reason and for the provided duration. Default Value: 10 minutes."
        ]
    elif help_request == "trust" or help_request == "trustlevel" or help_request == "alt":
        output = [
            f"**.trust**\n",
            f"Category: Moderation\n"
            f"Permission Level: Manager `♦`\n"
            f"Aliases: `.trust` `.trustlevel` `.alt`\n"
            f"Syntax: `.trust <user/id>`\n"
            f"\nShows the estimated trust level of that user to be an alt."
        ]
    elif help_request == "info" or help_request == "information":
        output = [
            f"**.info**\n",
            f"Category: Utility\n"
            f"Permission Level: User ` `\n"
            f"Aliases: `.info` `.information`\n"
            f"Syntax: `.info`\n"
            f"\nGives a bit of information about the bot."
        ]
    elif help_request == "commands" or help_request == "help":
        output = [
            f"**.commands**\n",
            f"Category: Utility\n"
            f"Permission Level: User ` `\n"
            f"Aliases: `.commands` `.help`\n"
            f"Syntax: `.commands [command]`\n"
            f"\nPulls up the help menu."
        ]
    elif help_request == "givexp":
        output = [
            f"**.givexp**\n",
            f"Category: Utility\n"
            f"Permission Level: Manager `♦`\n"
            f"Aliases: `.givexp`\n"
            f"Syntax: `.givexp <user/id> [amount]`\n"
            f"\nGives the specified amount of XP to the user."
        ]
    elif help_request == "userinfo" or help_request == "ui" or help_request == "whois":
        output = [
            f"**.userinfo**\n",
            f"Category: Utility\n"
            f"Permission Level: User ` `\n"
            f"Aliases: `.userinfo` `.ui` `.whois`\n"
            f"Syntax: `.userinfo <user/id>`\n"
            f"\nPulls up information about a user. Only works with users in this server."
        ]
    elif help_request == "serverinfo" or help_request == "si":
        output = [
            f"**.serverinfo**\n",
            f"Category: Utility\n"
            f"Permission Level: User ` `\n"
            f"Aliases: `.serverinfo` `.si`\n"
            f"Syntax: `.serverinfo`\n"
            f"\nPulls up information about this server."
        ]
    elif help_request == "afk" or help_request == "brb" or help_request == "gn" or help_request == "cya":
        output = [
            f"**.afk**\n",
            f"Category: Utility\n"
            f"Permission Level: User ` `\n"
            f"Aliases: `.afk` `.brb` `.gn` `.cya`\n"
            f"Syntax: `.afk`\n"
            f"\nMarks you globally AFK and changes the nickname where you send the command. When you send a new message, you will be set to not-AFK."
        ]
    elif help_request == "iss" or help_request == "space" or help_request == "spacestation":
        output = [
            f"**.iss**\n",
            f"Category: Fun\n"
            f"Permission Level: User ` `\n"
            f"Aliases: `.iss` `.space` `.spacestation`\n"
            f"Syntax: `.iss`\n"
            f"\nGives live information about the International Space Station."
        ]
    elif help_request == "dice" or help_request == "die" or help_request == "roll":
        output = [
            f"**.dice**\n",
            f"Category: Fun\n"
            f"Permission Level: User ` `\n"
            f"Aliases: `.dice` `.die` `.roll`\n"
            f"Syntax: `.dice [sides] [rolls] [bonus]`\n"
            f"\nRolls a dice. Allows for up to 1000 sides and 64 rolls."
        ]
    elif help_request == "coin" or help_request == "flip":
        output = [
            f"**.coin**\n",
            f"Category: Fun\n"
            f"Permission Level: User ` `\n"
            f"Aliases: `.coin` `.flip`\n"
            f"Syntax: `.coin`\n"
            f"\nFlips a virtual coin that shows either Heads or Tails."
        ]    
    elif help_request == "noise" or help_request == "random":
        output = [
            f"**.random**\n",
            f"Category: Fun\n"
            f"Permission Level: User ` `\n"
            f"Aliases: `.random` `.noise`\n"
            f"Syntax: `.random`\n"
            f"\nGenerates a completly random floating point number between 0 and 1."
        ]
    elif help_request == "color" or help_request == "colour":
        output = [
            f"**.color**\n",
            f"Category: Fun\n"
            f"Permission Level: User ` `\n"
            f"Aliases: `.color` `.colour`\n"
            f"Syntax: `.color`\n"
            f"\nGenerates a random color and pulls up a website to few it."
        ]  
    else:
        await ctx.send("I was unable to find the command you are looking for.")
  
    await ctx.send(''.join(output))

# Userinfo Command
@client.command(aliases=["ui", "whois"])
async def userinfo(ctx: commands.Context, user_id=empty_argument):

    # Check if Syntax is complete
    if user_id == empty_argument:
        user_id = str(ctx.message.author.id)
    
    # Prepare Command
    try:
        user_id = user_id.strip("<@>").strip()
        user_to_check = await client.fetch_user(user_id)
        user_to_check_guild = await ctx.guild.fetch_member(user_id)
        server_id = ctx.message.guild.id
        perm_level = f""
    except:
        await ctx.send("I was unable to fufill your command. Are you attempting to do this on a user not in this server?")    

    # Perm Level
    if not os.path.exists(f"servers/{server_id}/permissions"):
        os.makedirs(f"servers/{server_id}/permissions")
        with open(f"servers/{server_id}/permissions/permissions.json", "w") as file:
            json.dump([], file)

    with open(f"servers/{server_id}/permissions/permissions.json", "r") as file:
        manager_array = json.load(file)

    bool_role = fiiral_checker_bot.main(user_to_check_guild._roles, manager_array)
    if bool_role == True:
        perm_level = f"Manager `♦`"
    else:
        perm_level = f"User ` `"

    if user_to_check_guild.guild_permissions.administrator == True:
        if perm_level == f"Manager `♦`":
            perm_level = f"Manager and Administrator `♦ #`"
        else:
            perm_level =  f"Administrator `#`"
    if int(user_id) == 588411714274459679:
        perm_level = f"Developer `⚙`"

    try:
        if user_to_check.public_flags.hypesquad_balance:
            user_hypesquad = "Balance"
        elif user_to_check.public_flags.hypesquad_bravery:
            user_hypesquad = "Bravery"
        elif user_to_check.public_flags.hypesquad_brilliance:
            user_hypesquad = "Briliance"
        else:
            user_hypesquad = "No Hypesquad"
    except:
        user_hypesquad = "No Hypesquad"

    a = 0.05
    b = 1
    c = 6
    d = -server_xp_data[server_id][str(user_id)]
        
    # Use the cubic formula to solve for x
    p = (3*a*c - b**2) / (3*a**2)
    q = (2*b**3 - 9*a*b*c + 27*a**2*d) / (27*a**3)
    delta = (q/2)**2 + (p/3)**3
        
    u = math.pow(-q/2 + math.sqrt(delta), 1/3)
    v = math.pow(-q/2 - math.sqrt(delta), 1/3)
        
    user_level = u + v - b/(3*a)

    user_info = [
        f"**{user_to_check.name}#{user_to_check.discriminator}**\n",
        f"Activity: Level {math.floor(user_level)} with {server_xp_data[server_id][str(user_id)]}XP\n"
        f"Nickname: {user_to_check_guild.nick}\n",
        f"Status: {user_to_check_guild.status}\n"
        f"Hype Squad: {user_hypesquad}\n"
        f"Joined Discord: {user_to_check_guild.created_at.strftime('%d-%m-%Y at %H:%M')}\n",
        f"Joined Server: {user_to_check_guild.joined_at.strftime('%d-%m-%Y at %H:%M')}\n",
        f"Highest Role: {user_to_check_guild.top_role}\n",
        f"Access Level: {perm_level}\n" 
        f"Avatar: {user_to_check.avatar}"
    ]

    await ctx.send(''.join(user_info))

# Serverinfo Command
@client.command(aliases=["si"])
async def serverinfo(ctx: commands.Context):
    owner = await ctx.guild.fetch_member(ctx.guild.owner_id)

    if ctx.guild.premium_tier == 0:
        nitro_status = "Not Boosted"
    elif ctx.guild.premium_tier == 1:
        nitro_status = "Basic Boosted (Tier 1)"    
    elif ctx.guild.premium_tier == 2:
        nitro_status = "Super Boosted (Tier 2)"   
    elif ctx.guild.premium_tier == 3:
        nitro_status = "Hyper Boosted (Tier 3)"  

    server_info = [
        f"**{ctx.guild.name}**\n",
        f"Owner: {owner}\n",
        f"Server Creation: {owner.joined_at.strftime('%d-%m-%Y at %H:%M')}\n",
        f"Nitro Status: {nitro_status}\n",
        f"Member Count: {ctx.guild.member_count}\n",
        f"Channel Count: {len(ctx.guild.text_channels) + len(ctx.guild.voice_channels)}\n",
        f"Text Channel Count: {len(ctx.guild.text_channels)}\n",
        f"Voice Channel Count: {len(ctx.guild.voice_channels)}\n",
        f"Icon: {ctx.guild.icon}"
    ]

    await ctx.send(''.join(server_info))

# Give XP Command (Manager+)
@client.command("givexp")
async def givexp(ctx: commands.Context, user_id=empty_argument, xp_to_give=1):
    
    # Check if Syntax is complete
    if user_id == empty_argument:
        await ctx.send("I was unable to fufill your command because of incomplete syntax. Proper syntax: `.givexp <user/id> [amount]`")
        return
    
    # Prepare Command
    server_id = ctx.guild.id
    user_id = user_id.strip("<@>").strip()

    if server_id not in server_xp_data:
        server_xp_data[server_id] = {}

        if os.path.exists(f"servers/{server_id}/leveling"):
            with open(f"servers/{server_id}/leveling/xp_data.json", "r") as file:
                server_xp_data[server_id] = json.load(file)
        else:
            os.makedirs(f"servers/{server_id}/leveling")
            with open(f"servers/{server_id}/leveling/xp_data.json", "w") as file:
                json.dump({}, file)

    # Check if user XP data is already in memory, if not, create a new entry
    if str(user_id) not in server_xp_data[server_id]:
        server_xp_data[server_id][str(user_id)] = int(xp_to_give)
    else:
        server_xp_data[server_id][str(user_id)] += int(xp_to_give)

    await ctx.send(f"Gave the user {xp_to_give} XP")


################
# Fun Commands #
################

# Dice Roll Command
@client.command(aliases=["die", "roll"])
async def dice(ctx: commands.Context, dice="6", amount="1", bonus="0"):
    if int(amount) > 64:
        amount = 64
    elif int(amount) < 1:
        amount = 1

    if int(dice) > 1000:
        dice = 1000
    elif int(dice) < 2:
        dice = 2

    if int(amount) == 1:
        result = random.randint(1, int(dice)) + int(bonus)
        await ctx.send(f"You rolled a {result} with your dice!")  
    else:
        results = []
        for i in range(0,int(amount)):
            result = random.randint(1, int(dice)) + int(bonus)
            results.append(result)

        await ctx.send(f"You rolled a {results} with your dice!")
  
# Noise Command
@client.command(aliases=["random"])
async def noise(ctx: commands.Context):

    result = random.random()
    await ctx.send(f"You generated a noise of {result}!")  

# Flip Command
@client.command(aliases=["flip"])
async def coin(ctx: commands.Context):

    result = random.randint(0,1)
    if result == 1:
        result = "Heads"
    if result == 0:
        result = "Tails"

    await ctx.send(f"Your coin shows {result}!")  

# Color Command
@client.command(aliases=["colour"])
async def color(ctx: commands.Context):

    result = random.randint(0,16777215)
    result = "0x%0.6X" % result
    result = result.strip("0x").strip()
    website = result
    result = "#" + result

    await ctx.send(f"Your generated the color {result}!\nYou can look at it here: https://www.color-hex.com/color/{website}")  

# ISS Info Command
@client.command(aliases=["space", "spacestation"])
async def iss(ctx: commands.Context):
    loc = ISS_Info.iss_current_loc()
    crew = ISS_Info.iss_people_in_space()

    longitude = loc["iss_position"]["longitude"]
    latitude = loc["iss_position"]["latitude"]
    crew_size = crew["number"]

    information = [
        f"**Information about the International Space Station**\n"
        f"Longitude {longitude}\n",
        f"Latitude {latitude}\n",
        f"Crew Size: {crew_size}\n\n"
        f"Crew:\n"
    ]
    
    temp_info = []
    for person in crew["people"]:
        astronaut_info = person['name'] + ' is currently on the ' + person['craft']
        temp_info.append(astronaut_info)
    
    information.append('\n'.join(temp_info))
    information.append(f"\n\nNASA Livesteam: https://www.youtube.com/watch?v=itdpuGHAcpg")

    await ctx.send(''.join(information))

# AFK Command
@client.command(aliases=["brb", "gn", "cya"])
async def afk(ctx: commands.Context):

    afk_users[str(ctx.author.id)] = True
    with open(f"global/afk/afk.json", "w") as file:
        json.dump(afk_users, file)

    current_nick = ctx.author.nick
    await ctx.send(f"{ctx.author.mention} has gone afk.")
    try:
        await ctx.author.edit(nick=f"[AFK] {current_nick}")
    except:
        pass

###########################
# Administration Commands #
###########################

# Set Manager Command (Admin+)
@client.command(aliases=["setmoderator", "setmod", "addmanager", "addmoderator", "addmod"])
async def setmanager(ctx: commands.Context, role_id=empty_argument):

    # Check if Syntax is complete
    if role_id == empty_argument:
        await ctx.send("I was unable to fufill your command because of incomplete syntax. Proper syntax: `.setmanager <role/id>`")
        return

    if ctx.message.author.guild_permissions.administrator == True:
        server_id = ctx.message.guild.id
        role_id = role_id.strip("<@&>").strip()

        result = fiiral_bot_setmanager.main(server_id, role_id)
        await ctx.send(result)
    else:
        result = f"You need administrator permissions (#) to do this!"
        await ctx.send(result)

# Delete Manager Command (Admin+)
@client.command(aliases=["delmoderator", "delmod", "removemanager", "removemoderator", "removemod"])
async def delmanager(ctx: commands.Context, role_id=empty_argument):

    # Check if Syntax is complete
    if role_id == empty_argument:
        await ctx.send("I was unable to fufill your command because of incomplete syntax. Proper syntax: `.delmanager <role/id>`")
        return
    
    if ctx.message.author.guild_permissions.administrator == True:
        server_id = ctx.message.guild.id
        role_id = role_id.strip("<@&>").strip()

        result = fiiral_bot_delmanager.main(server_id, role_id)
        await ctx.send(result)
    else:
        result = f"You need administrator permissions (#) to do this!"
        await ctx.send(result)

# Server Backup Command (Admin+)
@client.command("serverbackup")
async def userbackup(ctx: commands.Context):
    if ctx.message.author.guild_permissions.administrator == True:
        server_id = ctx.guild.id

        key = Fernet(b'bQG938RWdMyECb7Mujsz6bgcYmxnSIT1FNYjK5u-w-4=')
        server_key = key.encrypt(str(server_id).encode("utf-8"))

        if os.path.exists(f"servers/{server_id}/leveling"):
            disc_file = discord.File(f"./servers/{server_id}/leveling/xp_data.json", filename='xp_data.json')
            await ctx.send(content="", file=disc_file)
        if os.path.exists(f"servers/{server_id}/permissions"):
            disc_file = discord.File(f"./servers/{server_id}/permissions/permissions.json", filename='permissions.json')
            await ctx.send(content="", file=disc_file)
        if os.path.exists(f"servers/{server_id}/warns"):
            disc_file = discord.File(f"./servers/{server_id}/warns/warns.json", filename='warns.json')
            await ctx.send(content="", file=disc_file)
        
        await ctx.send(f"All of these files are you server information. If you want to restore them at a later date you need a serverkey. This is done so that the server that it will be added to can be uniquely identified. Your serverkey is `{server_key}`\nDo **NOT** share this key.")
    else:
        result = f"You need administrator permissions (#) to do this!"
        await ctx.send(result)     


#######################
# Moderation Commands #
#######################

# Warn Command (Manager+)
@client.command("warn")
async def warn(ctx: commands.Context, user_warnee=empty_argument):

    # Check if Syntax is complete
    if user_warnee == empty_argument:
        await ctx.send("I was unable to fufill your command because of incomplete syntax. Proper syntax: `.warn <user/id>`")
        return

    # Prepare Command
    server_id = ctx.message.guild.id
    user_warnee = user_warnee.strip("<@>").strip()
    user_warner_roles = ctx.message.author._roles

    result = fiiral_bot_warn.main(server_id, user_warnee, user_warner_roles)
    await ctx.send(result)

# Unwarn Command (Manager+)
@client.command(aliases=["removewarn", "clearwarn"])
async def unwarn(ctx: commands.Context, user_to_remove=empty_argument, amount_to_remove=1):

    # Check if Syntax is complete
    if user_to_remove == empty_argument:
        await ctx.send("I was unable to fufill your command because of incomplete syntax. Proper syntax: `.unwarn <user/id> [amount]`")
        return

    # Prepare Command
    server_id = ctx.message.guild.id
    user_to_remove = user_to_remove.strip("<@>").strip()
    user_warner_roles = ctx.message.author._roles

    result = fiiral_bot_unwarn.main(server_id, user_to_remove, user_warner_roles, amount_to_remove)
    await ctx.send(result)

# Showwarns Command
@client.command(aliases=["showwarn"])
async def showwarns(ctx: commands.Context, user_to_show=empty_argument):

    # Check if Syntax is complete
    if user_to_show == empty_argument:
        await ctx.send("I was unable to fufill your command because of incomplete syntax. Proper syntax: `.showwarns <user/id>`")
        return

    # Prepare Command
    server_id = ctx.message.guild.id
    user_to_show = user_to_show.strip("<@>").strip()

    result = fiiral_bot_showwarns.main(server_id, user_to_show)
    await ctx.send(result)

# Showwarns Command
@client.command(aliases=["punish"])
async def autopunish(ctx: commands.Context, user_to_punish=empty_argument):

    # Check if Syntax is complete
    if user_to_punish == empty_argument:
        await ctx.send("I was unable to fufill your command because of incomplete syntax. Proper syntax: `.showwarns <user/id>`")
        return

    # Prepare Command
    server_id = ctx.message.guild.id
    user_to_punish = user_to_punish.strip("<@>").strip()
    user_warner_roles = ctx.message.author._roles
    warns = fiiral_bot_autopunish.main(server_id, user_to_punish, user_warner_roles)

    if warns == None:
        await ctx.send(f"You need manager permissions (♦) to do this!")

    user = await ctx.guild.fetch_member(user_to_punish)

    if warns == 0:
        await ctx.send(f"User had {warns} warnings. Punishment Level: **None**.")
        return
    elif warns == 1:
        await user.timeout(timedelta(minutes= 10), reason=f"Autopunished by {ctx.message.author.name} (ID: {ctx.message.author.id}) using Fiiral Bot.")
        await ctx.send(f"User had {warns} warnings. Punishment Level: **Minimal**.")
        return	
    elif warns == 2:
        await user.timeout(timedelta(minutes= 60), reason=f"Autopunished by {ctx.message.author.name} (ID: {ctx.message.author.id}) using Fiiral Bot.")
        await ctx.send(f"User had {warns} warnings. Punishment Level: **Light**.")
        return	
    elif warns == 3 or warns == 4:
        await user.timeout(timedelta(minutes= 720), reason=f"Autopunished by {ctx.message.author.name} (ID: {ctx.message.author.id}) using Fiiral Bot.")
        await ctx.send(f"User had {warns} warnings. Punishment Level: **Moderate**.")
        return	
    elif warns == 5 or warns == 6:
        await ctx.guild.kick(user, reason=f"Autopunished by {ctx.message.author.name} (ID: {ctx.message.author.id}) using Fiiral Bot.")
        await ctx.send(f"User had {warns} warnings. Punishment Level: **Severe**.")
        return
    elif warns >= 7:
        await ctx.guild.ban(user,reason=f"Autopunished by {ctx.message.author.name} (ID: {ctx.message.author.id}) using Fiiral Bot.", delete_message_seconds=604800)
        await ctx.send(f"User had {warns} warnings. Punishment Level: **Capital**.")
        return

# Kick Command (Manager+)
@client.command("purge")
async def purge(ctx: commands.Context, amount=1, *custom_reason):

    # Maximum to delete
    if amount > 100:
        amount = 100

    # Prepare Command
    try:
        user_kicker_roles = ctx.message.author._roles
        server_id = ctx.message.guild.id
    except:
        await ctx.send("I was unable to fufill your command. Are you attempting to do this in an empty server?")
        return

    custom_reason = ' '.join(custom_reason)

    # Checks if the file path exists and if not, makes a .json file.
    if not os.path.exists(f"servers/{server_id}/permissions"):
        os.makedirs(f"servers/{server_id}/permissions")
        with open(f"servers/{server_id}/permissions/permissions.json", "w") as file:
            json.dump([], file)
    
    # Loads the permissions.json file as an array.
    with open(f"servers/{server_id}/permissions/permissions.json", "r") as file:
        manager_array = json.load(file)
    
    if fiiral_checker_bot.main(user_kicker_roles, manager_array) == True:
        await ctx.message.channel.purge(limit=amount, reason=f"Purged by {ctx.message.author.name} (ID: {ctx.message.author.id}) using Fiiral Bot. Reason: {custom_reason}.")
        await ctx.send(f"Purged the last {amount} messages.")
    else:
        await ctx.send(f"You need manager permissions (♦) to do this!")

# Kick Command (Manager+)
@client.command("kick")
async def kick(ctx: commands.Context, user_to_kick=empty_argument, *custom_reason):

    # Check if Syntax is complete
    if user_to_kick == empty_argument:
        await ctx.send("I was unable to fufill your command because of incomplete syntax. `.kick <user/id> [reason]`")
        return

    # Prepare Command
    try:
        user_to_kick = user_to_kick.strip("<@>").strip()
        user_kicker_roles = ctx.message.author._roles
        server_id = ctx.message.guild.id
    except:
        await ctx.send("I was unable to fufill your command. Are you attempting to do this on a user not in this server?")
        return

    custom_reason = ' '.join(custom_reason)

    # Checks if the file path exists and if not, makes a .json file.
    if not os.path.exists(f"servers/{server_id}/permissions"):
        os.makedirs(f"servers/{server_id}/permissions")
        with open(f"servers/{server_id}/permissions/permissions.json", "w") as file:
            json.dump([], file)
    
    # Loads the permissions.json file as an array.
    with open(f"servers/{server_id}/permissions/permissions.json", "r") as file:
        manager_array = json.load(file)
    
    if fiiral_checker_bot.main(user_kicker_roles, manager_array) == True:
        user = await client.fetch_user(user_to_kick)
        await ctx.message.guild.kick(user, reason=f"Kicked by {ctx.message.author.name} (ID: {ctx.message.author.id}) using Fiiral Bot. Reason: {custom_reason}.")
        await ctx.send(f"Kicked that user.")
    else:
        await ctx.send(f"You need manager permissions (♦) to do this!")

# Ban Command (Manager+)
@client.command("ban")
async def ban(ctx: commands.Context, user_to_ban=empty_argument, *custom_reason):

    # Check if Syntax is complete
    if user_to_ban == empty_argument:
        await ctx.send("I was unable to fufill your command because of incomplete syntax. `.ban <user/id> [reason]`")
        return

    # Prepare Command
    try:
        user_to_ban = user_to_ban.strip("<@>").strip()
        user_kicker_roles = ctx.message.author._roles
        server_id = ctx.message.guild.id
    except:
        await ctx.send("I was unable to fufill your command. Are you attempting to do this on a user not in this server?")    

    custom_reason = ' '.join(custom_reason)

    # Checks if the file path exists and if not, makes a .json file.
    if not os.path.exists(f"servers/{server_id}/permissions"):
        os.makedirs(f"servers/{server_id}/permissions")
        with open(f"servers/{server_id}/permissions/permissions.json", "w") as file:
            json.dump([], file)
    
    # Loads the permissions.json file as an array.
    with open(f"servers/{server_id}/permissions/permissions.json", "r") as file:
        manager_array = json.load(file)
    
    if fiiral_checker_bot.main(user_kicker_roles, manager_array) == True:
        user = await client.fetch_user(user_to_ban)
        await ctx.message.guild.ban(user, reason=f"Banned by {ctx.message.author.name} (ID: {ctx.message.author.id}) using Fiiral Bot. Reason: {custom_reason}.", delete_message_seconds=604800)
        await ctx.send(f"Banned that user.")
    else:
        await ctx.send(f"You need manager permissions (♦) to do this!")

# Softban Command (Manager+)
@client.command("softban")
async def softban(ctx: commands.Context, user_to_ban=empty_argument, *custom_reason):

    # Check if Syntax is complete
    if user_to_ban == empty_argument:
        await ctx.send("I was unable to fufill your command because of incomplete syntax. `.softban <user/id> [reason]`")
        return

    # Prepare Command
    try:
        user_to_ban = user_to_ban.strip("<@>").strip()
        user_kicker_roles = ctx.message.author._roles
        server_id = ctx.message.guild.id
    except:
        await ctx.send("I was unable to fufill your command. Are you attempting to do this on a user not in this server?")    

    custom_reason = ' '.join(custom_reason)

    # Checks if the file path exists and if not, makes a .json file.
    if not os.path.exists(f"servers/{server_id}/permissions"):
        os.makedirs(f"servers/{server_id}/permissions")
        with open(f"servers/{server_id}/permissions/permissions.json", "w") as file:
            json.dump([], file)
    
    # Loads the permissions.json file as an array.
    with open(f"servers/{server_id}/permissions/permissions.json", "r") as file:
        manager_array = json.load(file)
    
    if fiiral_checker_bot.main(user_kicker_roles, manager_array) == True:
        user = await client.fetch_user(user_to_ban)
        await ctx.message.guild.ban(user, reason=f"Softbanned by {ctx.message.author.name} (ID: {ctx.message.author.id}) using Fiiral Bot. Reason: {custom_reason}.", delete_message_days=0)
        await ctx.send(f"Softbanned that user.")
    else:
        await ctx.send(f"You need manager permissions (♦) to do this!")

# Unban Command (Manager+)
@client.command("unban")
async def unban(ctx: commands.Context, user_to_unban=empty_argument, *custom_reason):

    # Check if Syntax is complete
    if user_to_unban == empty_argument:
        await ctx.send("I was unable to fufill your command because of incomplete syntax. `.unban <user/id> [reason]`")
        return

    # Prepare Command
    try:
        user_to_unban = user_to_unban.strip("<@>").strip()
        user_kicker_roles = ctx.message.author._roles
        server_id = ctx.message.guild.id
    except:
        await ctx.send("I was unable to fufill your command. Are you attempting to do this on a user not in this server?")    

    custom_reason = ' '.join(custom_reason)

    # Checks if the file path exists and if not, makes a .json file.
    if not os.path.exists(f"servers/{server_id}/permissions"):
        os.makedirs(f"servers/{server_id}/permissions")
        with open(f"servers/{server_id}/permissions/permissions.json", "w") as file:
            json.dump([], file)
    
    # Loads the permissions.json file as an array.
    with open(f"servers/{server_id}/permissions/permissions.json", "r") as file:
        manager_array = json.load(file)
    
    if fiiral_checker_bot.main(user_kicker_roles, manager_array) == True:
        user = await client.fetch_user(user_to_unban)
        await ctx.message.guild.unban(user, reason=f"Unbanned by {ctx.message.author.name} (ID: {ctx.message.author.id}) using Fiiral Bot. Reason: {custom_reason}.")
        await ctx.send(f"Unbanned that user.")
    else:
        await ctx.send(f"You need manager permissions (♦) to do this!")

# Timeout Command (Manager+)
@client.command(aliases=["timeout"])
async def mute(ctx: commands.Context, user_to_mute=empty_argument, time_minutes=10, *custom_reason):

    # Check if Syntax is complete
    if user_to_mute == empty_argument:
        await ctx.send("I was unable to fufill your command because of incomplete syntax. `.mute <user/id> [duration] [reason]`")
        return

    # Prepare Command
    try:
        user_to_mute = user_to_mute.strip("<@>").strip()
        user_kicker_roles = ctx.message.author._roles
        server_id = ctx.message.guild.id
    except:
        await ctx.send("I was unable to fufill your command. Are you attempting to do this on a user not in this server?")
        return

    custom_reason = ' '.join(custom_reason)

    # Checks if the file path exists and if not, makes a .json file.
    if not os.path.exists(f"servers/{server_id}/permissions"):
        os.makedirs(f"servers/{server_id}/permissions")
        with open(f"servers/{server_id}/permissions/permissions.json", "w") as file:
            json.dump([], file)
    
    # Loads the permissions.json file as an array.
    with open(f"servers/{server_id}/permissions/permissions.json", "r") as file:
        manager_array = json.load(file)
    
    if fiiral_checker_bot.main(user_kicker_roles, manager_array) == True:
        user = await ctx.guild.fetch_member(user_to_mute)
        await user.timeout(timedelta(minutes= int(time_minutes)), reason=f"Timeouted by {ctx.message.author.name} (ID: {ctx.message.author.id}) using Fiiral Bot. Reason: {custom_reason}.")
        await ctx.send(f"Timeouted that user.")
    else:
        await ctx.send(f"You need manager permissions (♦) to do this!")

# Trust Command (Manager+)
@client.command(aliases=["trustlevel", "alt"])
async def trust(ctx: commands.Context, user_id=empty_argument):

    # Check if Syntax is complete
    if user_id == empty_argument:
        await ctx.send("I was unable to fufill your command because of incomplete syntax. `.trust <user/id>`")
        return

    # Prepare Command
    try:
        user_id = user_id.strip("<@>").strip()
        user_to_check = await client.fetch_user(user_id)
        user_to_check_guild = await ctx.guild.fetch_member(user_id)
        user_truster_roles = ctx.message.author._roles
        trust = 0
        server_id = ctx.message.guild.id
    except:
        await ctx.send("I was unable to fufill your command. Are you attempting to do this on a user not in this server?")
        return

    # Checks if the file path exists and if not, makes a .json file.
    if not os.path.exists(f"servers/{server_id}/permissions"):
        os.makedirs(f"servers/{server_id}/permissions")
        with open(f"servers/{server_id}/permissions/permissions.json", "w") as file:
            json.dump([], file)

    # Loads the permissions.json file as an array.
    with open(f"servers/{server_id}/permissions/permissions.json", "r") as file:
        manager_array = json.load(file)

    if fiiral_checker_bot.main(user_truster_roles, manager_array) == True:
        try:
            if user_to_check.public_flags.hypesquad_balance:
                trust += 1
            elif user_to_check.public_flags.hypesquad_bravery:
                trust += 1
            elif user_to_check.public_flags.hypesquad_brilliance:
                trust += 1
            else:
                trust += 0
        except:
            trust += 0
        
        try:
            if user_to_check.public_flags.spammer:
                trust -= 2
        except:
            trust += 0
        
        try:
            if user_to_check.avatar != user_to_check.default_avatar:
                trust += 1
        except:
            trust += 0
            
        time_difference = datetime.now().timestamp() - user_to_check_guild.created_at.timestamp()
        if time_difference > 86400:
            trust += 1
        if time_difference > 604800:
            trust += 1
        if time_difference > 7776000:
            trust += 1
        if time_difference > 31536000:
            trust += 1
        if time_difference > 126144000:
            trust += 1

        if trust == 0 or trust == 1:
            trust_result = "Severely Distrusted"
        if trust == 2 or trust == 3:
            trust_result = "Distrusted"
        if trust == 4:
            trust_result = "Average"
        if trust == 5:
            trust_result = "Trusted"
        if trust == 6:
            trust_result = "Very Trusted"
        if trust == 7:
            trust_result = "Extraordinarily Trusted"   

        await ctx.send(f"The User has a current trust rating of **{trust_result}**. Their exact rating is: {trust}.\nNote: This system cannot detect if a user has a verified email or 2FA enabled. This is due to hard limits of the Discord API.")
    else:
        await ctx.send(f"You need manager permissions (♦) to do this!")


#################
# XP & Leveling #
#################

# XP Saver Manager to save every 5 min
async def save_xp_data():
    while True:
        await asyncio.sleep(300)
        start_time = time.monotonic()

        for server_id, data in server_xp_data.items():
            with open(f"servers/{server_id}/leveling/xp_data.json", "w") as file:
                json.dump(data, file)
        
        end_time = time.monotonic()
        elapsed_time = end_time - start_time
        print(f"Wrote XP Data to the files. Process took {elapsed_time:.3f} seconds.")


# Testing
#client.run("TOKEN")
