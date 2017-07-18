from aiohttp import ClientSession
from collections import OrderedDict
from discord.ext import commands
from Cogs.Utils.Messages import makeEmbed
from Cogs.Utils.Configs import getTokens
from Cogs.Utils.PrintableMessage import PrintableMessage
from Cogs.Utils.Permissions import permissionChecker


class BotLogger(object):

    def __init__(self, sparcli:commands.Bot):
        self.sparcli = sparcli
        logChannel = getTokens()['BotLoggingChannel']
        self.discordBotsToken = getTokens()['DiscordBotsPw']['Key']
        self.logChannel = sparcli.get_channel(logChannel)
        self.session = ClientSession(loop=sparcli.loop)
        self.fserver = None

    def __unload(self):
        self.session.close()

    async def on_message(self, message):
        if self.fserver:
            if message.server == self.fserver:
                print(PrintableMessage(message))
        else:
            print(PrintableMessage(message))

    @commands.command(pass_context=True, hidden=True)
    @permissionChecker(check='is_owner')
    async def setfilter(self, ctx, *, serverName:str=None):
        if serverName:
            try:
                serverObj = [i for i in self.sparcli.servers if serverName in i.name][0]
                self.fserver = serverObj
                await self.sparcli.say('Done!')
            except IndexError:
                await self.sparcli.say('No can do, boss.')
        else:
            self.fserver = None 
            await self.sparcli.say('Done!')

    @commands.command(pass_context=True, hidden=True)
    @permissionChecker(check='is_owner')
    async def say(self, ctx, channelName:str, *, content:str):
        c = [i for i in self.fserver.channels if channelName in i.name][0]
        await self.sparcli.send_message(c, content)


    async def updateDiscordBots(self, serverAmount):
        '''
        Updates the Discord bots website
        '''

        if not self.discordBotsToken: return

        data = {
            'server_count': serverAmount
        }
        headers = {
            'Authorization': self.discordBotsToken
        }
        v = await self.session.post(
            'https://bots.discord.pw/api/bots/{}/stats'.format(self.sparcli.user.id),
            data=data,
            headers=headers
        )

    async def on_server_join(self, server):
        '''
        Triggered when the bot joins a server
        '''

        botServers = len(self.sparcli.servers)
        # await self.updateDiscordBots(botServers)

        allMembers = server.members 
        userMembers = len([i for i in allMembers if not i.bot])
        botMembers = len(allMembers) - userMembers

        o = OrderedDict()
        o['Server Name'] = server.name 
        o['Server Amount'] = botServers
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

        botServers = len(self.sparcli.servers)
        # await self.updateDiscordBots(botServers)

        allMembers = server.members 
        userMembers = len([i for i in allMembers if not i.bot])
        botMembers = len(allMembers) - userMembers

        o = OrderedDict()
        o['Server Name'] = server.name 
        o['Server Amount'] = botServers
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
