import discord
from discord import Embed

client = discord.Client()

token = None
with open("token.conf") as f:
    token = f.read()

serverConfig = None
with open("servers.conf") as f:
    serverConfig = eval(f.read())

mods = None
with open("mods.conf") as f:
    mods = eval(f.read())

prefix = "r!"

@client.event
async def on_ready():
    print(f'[Relayer] Started as {client.user}')

@client.event
async def on_guild_remove(guild):
    if guild.id in serverConfig.keys():
        del serverConfig[guild.id]
        with open("servers.conf", "w") as f:
                f.write(str(serverConfig))
                f.close()

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    content = message.content.replace("r!","")
    args = content.split(" ")

    if message.content.startswith("r!"):
        if args[0] in commands.keys():
            await commands[args[0]](message, args)
        return
    
    if message.guild.id in serverConfig.keys():
        if message.channel.id == serverConfig[message.guild.id]:
            for server in serverConfig.keys():
                for guild in client.guilds:
                    if server == guild.id:
                        for channel in guild.channels:
                            if channel.id == serverConfig[server]:
                                messageEmbed = Embed(description=content)
                                messageEmbed.set_author(icon_url=message.author.avatar_url, name=message.author.name)
                                date = str( message.created_at ).split(" ")[0]
                                msgtime = str( message.created_at ).split(" ")[1].split(".")[0]
                                messageEmbed.set_footer(text=f"{date}\n{msgtime}")
                                await channel.send(embed=messageEmbed)
                                break
                        break
            
        await message.delete()

async def setChannel(message, args):
    try: 
        channelid = args[1].replace("<#","").replace("!","").replace(">","")
        channelid = int(channelid)
    except:
        await message.channel.send(f"Couldn't find this channel.")
        return

    channelFound = False
    for channel in message.guild.channels:
        if channel.id == channelid:
            serverConfig[message.guild.id] = channelid
            with open("servers.conf", "w") as f:
                f.write(str(serverConfig))
                f.close()
            channelFound = True
            break

    if channelFound:
        await message.channel.send(f"Relay Channel set to {args[1]}.")
    else:
        await message.channel.send(f"Couldn't find this channel.")

async def help(message, args):
    await message.channel.send(f"Use `r!channel #channel` to setup an IRC Channel.")

async def servers(message, args):
    if not message.author.id in mods:
        return

    messageEmbed = Embed()
    for guild in client.guilds:
        messageEmbed.add_field(name=guild.name, value=guild.id)
    
    await message.channel.send(embed=messageEmbed)

async def leave(message, args):
    if not message.author.id in mods:
        return
    
    id = int(args[1])
    for guild in client.guilds:
        if guild.id == id:
            await guild.leave()
            break

commands = {
    "channel":setChannel,
    "servers":servers,
    "leave":leave,
    "help":help,
    "commands":help
}

client.run(token)