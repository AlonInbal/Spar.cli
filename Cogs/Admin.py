from aiohttp import ClientSession
from discord import Member
from discord.ext import commands
from Cogs.Utils.Permissions import permissionChecker, botPermission
from Cogs.Utils.Configs import getServerJson, saveServerJson


class Admin:

    def __init__(self, sparcli):
        self.sparcli = sparcli
        self.session = ClientSession(loop=sparcli.loop)

    def __unload(self):
        self.session.close()

    @commands.command(pass_context=True)
    @permissionChecker(check='ban_members', compare=True)
    @botPermission(check='ban_members', compare=True)
    async def ban(self, ctx, user:Member, *, reason:str=None):
        '''
        Bans a user from the server
        '''

        if reason == None:
            await self.sparcli.say('You must provide a reason for this.')
            return

        # Setup some local variables
        userToDo = user 
        author = ctx.message.author
        serverData = getServerJson(ctx.message.server.id)

        # Perform the actions in the local channel
        await self.sparcli.ban(userToDo)
        await self.sparcli.say('Done.')

        # See if you need to copy over to another channel
        if serverData['Toggles']['Bans']:

            # Generate a nice message
            toSay = ('**Ban**\n'
                     '**User:** {user} (`{user.id}`)\n'
                     '**Reason:** {reason}\n'
                     '**Moderator:** {moderator} (`{moderator.id}`)').format(user=userToDo, reason=reason, moderator=author)

            # Determine where to send it
            channelID = serverData['Channels']['Kicks']
            channelObject = ctx.message.server.get_channel(channelID) if channelID else ctx.message.server 

            # Boop
            await self.sparcli.send_message(channelObject, toSay)

    @commands.command(pass_context=True)
    @permissionChecker(check='kick_members', compare=True)
    @botPermission(check='kick_members', compare=True)
    async def kick(self, ctx, user:Member, *, reason:str=None):
        '''
        Kicks a user from the server
        '''

        if reason == None:
            await self.sparcli.say('You must provide a reason for this.')
            return

        # Setup some local variables
        userToDo = user 
        author = ctx.message.author
        serverData = getServerJson(ctx.message.server.id)

        # Perform the actions in the local channel
        await self.sparcli.kick(userToDo)
        await self.sparcli.say('Done.')

        # See if you need to copy over to another channel
        if serverData['Toggles']['Kicks']:

            # Generate a nice message
            toSay = ('**Kick**\n'
                     '**User:** {user} (`{user.id}`)\n'
                     '**Reason:** {reason}\n'
                     '**Moderator:** {moderator} (`{moderator.id}`)').format(user=userToDo, reason=reason, moderator=author)

            # Determine where to send it
            channelID = serverData['Channels']['Kicks']
            channelObject = ctx.message.server.get_channel(channelID) if channelID else ctx.message.server 

            # Boop
            await self.sparcli.send_message(channelObject, toSay)

    @commands.command(pass_context=True)
    @permissionChecker(check='manage_messages')
    @botPermission(check='manage_messages')
    async def purge(self, ctx, amount: int):
        '''
        Deletes a number of messages from a channel
        '''

        # Make sure the calling member isn't an idiot
        if amount >= 500:
            await self.sparcli.say('That number is too large. Please tone it down a notch.')
            return

        # Use the API's purge feature
        amount += 1
        deleted = await self.sparcli.purge_from(ctx.message.channel, limit=amount)
        deletedAmount = len(deleted)
        await self.sparcli.say('Removed `{}` messages.'.format(deletedAmount))

    @commands.command(pass_context=True)
    @permissionChecker(check='manage_nicknames', compare=True)
    @botPermission(check='manage_nicknames', compare=True)
    async def rename(self, ctx, user:Member, *, name:str=None):
        '''
        Changes the nickname of a member
        '''

        await self.sparcli.change_nickname(user, name)
        await self.sparcli.say('Name updated successfully.')

    @commands.group(pass_context=True)
    @permissionChecker(check='manage_nicknames', compare=True)
    @botPermission(check='manage_nicknames', compare=True)
    async def forcenickname(self, ctx):
        '''
        Forces a nickname on a user
        '''

        pass

    @forcenickname.command(pass_context=True, name='add')
    @permissionChecker(check='manage_nicknames', compare=True)
    @botPermission(check='manage_nicknames', compare=True)
    async def _add(self, ctx, user:Member, *, nickname:str=None):
        '''
        Lets you force a username on a user
        '''

        serverSettings = getServerJson(ctx.message.server.id)
        serverSettings['ForcedNicknames'][str(user.id)] = nickname
        saveServerJson(ctx.message.server.id, serverSettings)
        await self.sparcli.change_nickname(user, nickname)
        await self.sparcli.say('Nickname `{}` has been forced upon this user.'.format(nickname))

    @forcenickname.command(pass_context=True, name='remove', aliases=['del', 'delete', 'delet', 'rem'])
    @permissionChecker(check='manage_nicknames', compare=True)
    @botPermission(check='manage_nicknames', compare=True)
    async def _rem(self, ctx, user:Member):
        '''
        Removes a forced nickname from a user
        '''

        serverSettings = getServerJson(ctx.message.server.id)
        try:
            del serverSettings['ForcedNicknames'][str(user.id)]
        except KeyError:
            await self.sparcli.say('This user doesn\'t have a forced nickname.')
            return
        saveServerJson(ctx.message.server.id, serverSettings)
        await self.sparcli.change_nickname(user, None)
        await self.sparcli.say('All forced nicknames have been removed from this user.')

    @commands.command(pass_context=True, aliases=['servericon'])
    @permissionChecker(check='manage_server')
    @botPermission(check='manage_server')
    async def serverimage(self, ctx, *, icon:str=None):
        '''
        Changes the icon of the server
        '''

        # Sees if there's an image as an icon
        if icon != None:
            pass
        # Gets it from the attachments
        else:
            try:
                icon = ctx.message.attachments[0]['url']
            except (KeyError, IndexError):
                await self.sparcli.say('You need to pass an image to change the server icon to.')
                return

        # Sets it as the server image
        server = ctx.message.server
        iconContent = None
        async with self.session.get(icon) as r:
            iconContent = await r.content
            
        await self.sparcli.edit_server(server, icon=iconContent)
        await self.sparcli.say('Server icon has been updated.')


def setup(bot):
    bot.add_cog(Admin(bot))
