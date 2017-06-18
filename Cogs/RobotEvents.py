from aiohttp import ClientSession
from collections import OrderedDict
from urllib.parse import quote
from discord.ext import commands 
from Cogs.Utils.Messages import makeEmbed


class RobotEvents(object):

    def __init__(self, sparcli):
        self.sparcli = sparcli
        self.session = ClientSession(loop=sparcli.loop)

    def __unload(self):
        self.session.close()

    @commands.command(pass_context=True)
    async def vexteam(self, ctx, teamNumber:str):
        '''
        Gives you the information for a VEX team
        '''

        await self.sparcli.send_typing(ctx.message.channel)

        base = 'https://api.vexdb.io/v1/get_teams?team={}'
        team = quote(teamNumber, safe='')
        async with self.session.get(base.format(team)) as r:
            rawData = await r.json()
        data = rawData['result'][0]

        o = OrderedDict()
        o['Team Name'] = data['team_name']
        o['Team Number'] = data['number']
        o['Program'] = data['program']
        o['Robot Name'] = data['robot_name'] if data['robot_name'] else 'N/A'
        o['Organisation'] = data['organisation']
        o['Contry'] = data['country'] 
        o['Grade'] = data['grade']
        o['Registered'] = str(bool(data['is_registered']))
        em = makeEmbed(fields=o, author=data['team_name'])
        # em = makeEmbed(author='test')
        # await self.sparcli.say(o)
        await self.sparcli.say(embed=em)


def setup(bot):
    bot.add_cog(RobotEvents(bot))
