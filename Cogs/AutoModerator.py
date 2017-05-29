from discord.ext import commands
from Cogs.Utils.Configs import getServerJson


class AutoModerator:

    def __init__(self, sparcli):
        self.sparcli = sparcli

    async def deleteServerInvtes(self, message):
        '''
        Automatically delete server invites
        '''

        # Check the server configs
        serverSettings = getServerJson(message.server.id)
        deleteInvites = serverSettings['Toggles']['Deleteserverinvites']
        if not deleteInvites:
            return

        # See if the message contains a server invite
        splitMessage = message.content.lower().split('discord.gg/')
        if len(splitMessage) == 1:
            return

        # There's one or more server invite in there
        # Check for an existing invite code
        if len(splitMessage[1].split(' ')[0]) == 0:
            return

        # There's an invite code
        await self.sparcli.delete_message(message)
        

    async def on_message(self, message):
        await self.deleteServerInvtes(message)

    async def on_member_update(self, before, after):
        '''
        Check for any forced nicknames
        '''

        serverSettings = getServerJson(after.server.id)
        forcedNicknames = serverSettings['ForcedNicknames']

        # `forcedNicknames` is a {userID: nickname} pair
        try:
            toChangeTo = forcedNicknames[str(after.id)]
            if after.nick == toChangeTo:
                return
        except KeyError:
            return

        # `toChangeTo` is the nickname to change to
        await self.sparcli.change_nickname(after, toChangeTo)


def setup(bot):
    bot.add_cog(AutoModerator(bot))
