from discord.ext import commands 
from Cogs.Utils.Configs import getServerJson


class MemberManagement:

    def __init__(self, sparcli):
        self.sparcli = sparcli

    async def on_member_join(self, member):
        await self.sendChannelEnable(member, 'Joins')

        # Get the role ID
        serverSettings = getServerJson(member.server.id)
        if serverSettings['OnJoin'] and member.bot == False:
            role = serverSettings['OnJoin']
        elif serverSettings['OnBotJoin'] and member.bot == True:
            role = serverSettings['OnBotJoin']
        else:
            return

        # Get the role object
        roleObj = [i for i in member.server.roles if i.id == role][0]
        await self.sparcli.add_role(member, roleObj)

    async def on_member_remove(self, member):
        await self.sendChannelEnable(member, 'Leaves')

    async def sendChannelEnable(self, member, eventType):
        '''
        Sends a message to a specified channel if it is enabled in the server settings
        '''

        # Get the server settings
        serverSettings = getServerJson(member.server.id)

        # Determine whether the event messages are enabled or not
        joinsEnabled = serverSettings['Toggles'][eventType]
        if joinsEnabled == False:
            return

        # At this point, you know it's enabled, so we can go ahead and determine where
        # to send the message and what message to send
        sendText = serverSettings['Messages'][eventType]
        sendText = sendText.replace('{mention}', member.mention).replace('{name}', str(member))

        # Get the channel ID
        channelLocation = serverSettings['Channels'][eventType]
        if channelLocation == '':
            channelLocation = member.server.id 

        # Get the channel object
        channelObject = member.server.get_channel(channelLocation)
        if channelObject == None:
            return

        # Send the message
        await self.sparcli.send_message(channelObject, sendText)


def setup(bot):
    bot.add_cog(MemberManagement(bot))
