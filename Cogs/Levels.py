from math import log
from discord import Member
from discord.ext import commands 
from Cogs.Utils.LevelHandler import LevelHandler
from Cogs.Utils.Configs import getMoneyJson


class Levels:

    def __init__(self, sparcli):
        self.sparcli = sparcli
        self.levelHandler = LevelHandler()

    @commands.command(pass_context=True)
    async def xp(self, ctx, user:Member=None):
        '''
        Shows you how much experience you have
        '''

        if user == None:
            user = ctx.message.author

        serverXP = getMoneyJson(str(ctx.message.server.id))
        userXP = serverXP.get(str(user.id), 0)

        await self.sparcli.say('**{}** has **{}**XP on this server.'.format(user.display_name. userXP))

    @commands.command(pass_context=True)
    async def level(self, ctx, user:Member=None):
        '''
        Shows you how much experience you have
        '''

        if user == None:
            user = ctx.message.author

        serverXP = getMoneyJson(str(ctx.message.server.id))
        userXP = serverXP.get(str(user.id), 0)
        userLevel = userXP/375

        await self.sparcli.say('**{}** is level **{:.2f}** on this server.'.format(user.display_name, userLevel))

    @commands.command(pass_context=True)
    async def leaderboard(self, ctx):
        '''
        Shows you the top ten members on your server
        '''

        # Get all of the users in the server and reverse their values
        leaderboard = {i: o for o, i in getMoneyJson(str(ctx.message.server.id)).items()}

        # Get the total experience and sort it highest to lowest
        xpStains = [i for i in leaderboard.keys()]
        xpStains = sorted(xpStains, reverse=True)

        # Go through and get the first ten people (as IDs)
        lads = []
        for i in range(10):
            z = xpStains[i]
            lads.append([leaderboard[z], z])

        # Go through and convert all of those IDs into member objects
        ladz = []
        for i in lads:
            if ctx.message.server.get_member(i[0]):
                ladz.append([ctx.message.server.get_member(i[0]), i[1]])

        # Sort it all out into a nicely returnable string
        ret = ''
        for i in ladz:
            ret = ret + i[0].display_name + ' - **Lvl {:.2f}** \n'.format(i[1]/375)

        # Print it out to the user like a pleb
        await self.sparcli.say(ret)


    async def on_message(self, message):
        '''
        Message handler for level and exp increases
        '''

        self.levelHandler.increment(message)


def setup(bot):
    bot.add_cog(Levels(bot))
