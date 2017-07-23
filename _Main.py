from sys import argv
import discord
from discord.ext import commands
from Cogs.Utils.Configs import *
from Cogs.Utils.Updates import *
from Cogs.Utils.Messages import makeEmbed
from Cogs.Utils.Extentions import q as initialExtentions


def getCommandPrefix(bot, message):
    # Returns the command prefix of the server
    # Get the settings for the server
    try:
        serverSettings = getServerJson(message.server.id)
        serverPrefix = serverSettings['CommandPrefix']
    except AttributeError:
        return ['; ', ';', '<@252880131540910080> ']

    # Load the server prefix as defined
    return [serverPrefix + ' ', serverPrefix, '<@252880131540910080> ']


sparcli = commands.Bot(
    command_prefix=getCommandPrefix, 
    description='Another general purpose bot, but with quite a few more dumb fun commands.',
    pm_help=True, 
    formatter=commands.formatter.HelpFormatter(show_check_failure=True),
    max_messages=5000
)


@sparcli.event
async def on_guild_join(guild):
    # Runs when the bot joins a server
    # Create a config file for the server it joined
    z = getServerJson(guild.id)
    z = fixJson(z)
    saveServerJson(guild.id, z)

    # Say hi
    toSay = 'Hey! I\'ve just been added to this guild. I\'m Spar.cli, and I\'ll try and do a good job c;'
    try:
        await guild.default_channel.send_message(guild, toSay)
    except Exception:
        pass


@sparcli.event
async def on_message_edit(before, after):
    # Get the last message from the channel
    editedIDs = []
    async for message in after.history(limit=3):
        editedIDs.append(message.id)

    # Check if the edited message and the last few messages are the same;
    # if they are you can process that as a command
    if after.id in editedIDs:
        await sparcli.process_commands(after)


@sparcli.event
async def on_message(message):

    # Make the bot not respond to other bots
    if message.author.bot:
        return

    # Process commands
    await sparcli.process_commands(message)


@sparcli.event
async def on_ready():
    print('-----')
    print('User :: {}'.format(sparcli.user))
    print('ID :: {}'.format(sparcli.user.id))
    print('-----')

    # Load the extentions
    for extension in initialExtentions:
        # This is necessary because I'm bad at code lol
        try:
            sparcli.load_extension(extension)

        # Print out any errors
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            print('Failed to load extension {}\n{}'.format(extension, exc))

    # Load up any changes that would have been made to the configs
    for guild in sparcli.guilds:
        z = getServerJson(guild.id)
        z = fixJson(z)
        saveServerJson(guild.id, z)

    # Reccursively fix any globals too
    z = getServerJson('Globals')
    z = fixJson(z)
    saveServerJson('Globals', z)

    # Changed the bot's game
    game = '@Spar.cli help'
    g = discord.Game(name=game)
    await sparcli.change_presence(game=g)


sparcli.run(argv[1])
