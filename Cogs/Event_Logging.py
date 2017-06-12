from collections import OrderedDict
from discord.ext import commands
from Cogs.Utils.Messages import makeEmbed
from Cogs.Utils.Configs import getTokens


class BotLogger(object):

    def __init__(self, sparcli:commands.Bot):
        self.sparcli = sparcli
        logChannel = getTokens()['BotLoggingChannel']
        self.logChannel = sparcli.get_channel(logChannel)

    async def on_server_join(self, server):
        '''
        Triggered when the bot joins a server
        '''

        allMembers = server.members 
        userMembers = len([i for i in allMembers if not i.bot])
        botMembers = len(allMembers) - userMembers

        o = OrderedDict()
        o['Server Name'] = server.name 
        o['Server Amount'] = len(self.sparcli.servers)
        o['Server ID'] = server.id 
        o['Memebrs'] = '`{}` members (`{}` users, `{}` bots)'.format(
            len(allMembers),
            userMembers,
            botMembers
        )
        em = makeEmbed(author='Server Join!', fields=o, colour=0x228B22)
        await self.sparcli.send_message(
            self.logChannel,
            embed=em
        )

    async def on_server_remove(self, server):
        '''
        Triggered when the bot leaves a server
        '''

        allMembers = server.members 
        userMembers = len([i for i in allMembers if not i.bot])
        botMembers = len(allMembers) - userMembers

        o = OrderedDict()
        o['Server Name'] = server.name 
        o['Server Amount'] = len(self.sparcli.servers)
        o['Server ID'] = server.id 
        o['Memebrs'] = '`{}` members (`{}` users, `{}` bots)'.format(
            len(allMembers),
            userMembers,
            botMembers
        )
        em = makeEmbed(author='Server Leave :c', fields=o, colour=0xFF0000)
        await self.sparcli.send_message(
            self.logChannel,
            embed=em
        )


def setup(bot:commands.Bot):
    x = BotLogger(bot)
    bot.add_cog(x)
