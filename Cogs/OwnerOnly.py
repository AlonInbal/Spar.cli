from aiohttp import ClientSession
from sys import exit
from os import execl
from sys import exit, executable, argv, exc_info
from traceback import format_exception
from discord import Status
from discord.ext import commands
from Cogs.Utils.Permissions import permissionChecker
from Cogs.Utils.Configs import getServerJson, saveServerJson, fixJson
from Cogs.Utils.Extentions import q as initialExtentions


class OwnerOnly:

    def __init__(self, sparcli):
        self.sparcli = sparcli
        self.session = ClientSession(loop=sparcli.loop)

    def __unload(self):
        self.session.close()

    @commands.command(pass_context=True, hidden=True)
    @permissionChecker(check='is_owner')
    async def ev(self, ctx, *, content: str):
        '''
        Evaluates a given Python expression.
        '''

        # Eval and print the answer
        try:
            output = eval(content)
        except Exception:
            type_, value_, traceback_ = exc_info()
            ex = format_exception(type_, value_, traceback_)
            output = ''.join(ex)
        await self.sparcli.say('```python\n{}```'.format(output))

    @commands.command(pass_context=True, hidden=True)
    @permissionChecker(check='is_owner')
    async def ex(self, ctx, *, content: str):
        '''
        Executes a given Python expression.
        '''

        # Eval and print the answer
        try:
            exec(content)
            output = 'Done.'
        except Exception:
            type_, value_, traceback_ = exc_info()
            ex = format_exception(type_, value_, traceback_)
            output = ''.join(ex)
        await self.sparcli.say('```python\n{}```'.format(output))


    @commands.command(pass_context=True, hidden=True)
    @permissionChecker(check='is_owner')
    async def av(self, ctx, *, avatarUrl: str=None):
        '''
        Changes the bot's avatar to a set URL.
        '''

        # Checks for the URL - either passed as argument or embed
        try:
            if avatarUrl == None:
                avatarUrl = ctx.message.attachments[0]['url']
        except IndexError:
            # If you get to this point, there's no image
            await self.sparcli.say('You need to pass an image or url to set the avatar to.')
            return

        # Load up the image
        async with self.session.get(avatarUrl) as r:
            imageData = await r.content

        # Set profile picture
        await self.sparcli.edit_profile(avatar=imageData)
        await self.sparcli.say("Profile picture successfully changed.")

    @commands.command(pass_context=True, hidden=True)
    @permissionChecker(check='is_owner')
    async def kill(self, ctx):
        '''
        Kills the bot. Makes it deaded.
        '''

        # If it is, tell the user the bot it dying
        await self.sparcli.say('*Finally*.')
        await self.sparcli.change_presence(status=Status.invisible, game=None)
        exit()

    @commands.command(pass_context=True, hidden=True)
    @permissionChecker(check='is_owner')
    async def rld(self, ctx, toLoad: str=None, doFully:str=False):
        '''
        Reload an extention on the bot.
        '''

        # Get list of loaded extentions
        if toLoad == None:
            await self.sparcli.say("Currently loaded extentions :: \n```\n{}```".format("\n".join(self.sparcli.cogs)))
            return

        # Decides whether to be a smartbot
        if doFully:
            extention = 'Cogs.' + extention 

        else:
            loadedCogs = list(self.sparcli.cogs.keys())
            toLoad = [i for i in loadedCogs if toLoad.lower() in i.lower()]
            try:
                extention = 'Cogs.{}'.format(toLoad[0])
            except IndexError:
                await self.sparcli.say('There is no extention by that name.')
                return

        # Unload the extention
        await self.sparcli.say("Reloading extension **{}**...".format(extention))
        try:
            self.sparcli.unload_extension(extention)
        except:
            pass

        # Load the new one
        try:
            self.sparcli.load_extension(extention)
        except Exception:
            type_, value_, traceback_ = exc_info()
            ex = format_exception(type_, value_, traceback_)
            output = ''.join(ex)
            await self.sparcli.say('```python\n{}```'.format(output))
            return

        # Boop the user
        await self.sparcli.say("Done!")

    @commands.command(pass_context=True, hidden=True)
    @permissionChecker(check='is_owner')
    async def uld(self, ctx, toLoad: str=None, doFully:str=False):
        '''
        Reload an extention on the bot.
        '''

        # Get list of loaded extentions
        if toLoad == None:
            await self.sparcli.say("Currently loaded extentions :: \n```\n{}```".format("\n".join(self.sparcli.cogs)))
            return

        # Decides whether to be a smartbot
        if doFully:
            extention = 'Cogs.' + extention 

        else:
            loadedCogs = list(self.sparcli.cogs.keys())
            toLoad = [i for i in loadedCogs if extention.lower() in i.lower()]
            try:
                extention = 'Cogs.{}'.format(toLoad[0])
            except IndexError:
                await self.sparcli.say('There is no extention by that name.')
                return

        # Unload the extention
        await self.sparcli.say("Unloading extension **{}**...".format(extention))
        try:
            self.sparcli.unload_extension(extention)
        except:
            pass

        # Boop the user
        await self.sparcli.say("Done!")

    @commands.command(pass_context=True, hidden=True)
    @permissionChecker(check='is_owner')
    async def loadmessage(self, ctx, messageID: str):
        '''
        Loads a message into the bot chache.
        '''

        # Find and add the message
        messageToAdd = await self.sparcli.get_message(ctx.message.channel, messageID)
        self.sparcli.messages.append(messageToAdd)
        await self.sparcli.say('This message has been added to the bot\'s cache.')

    @commands.command(pass_context=True, hidden=True, aliases=['rs'])
    @permissionChecker(check='is_owner')
    async def restart(self, ctx):
        '''
        Restarts the bot. Literally everything.
        '''

        # If it is, tell the user the bot it dying
        await self.sparcli.say('Now restarting.')
        await self.sparcli.change_presence(status=Status.dnd, game=None)
        execl(executable, *([executable] + argv))

    @commands.command(pass_context=True, hidden=True)
    @permissionChecker(check='is_owner')
    async def serverinvite(self, ctx, *, serverName:str):
        '''
        Gets an invite for a given server's name.
        '''

        serverName = serverName.casefold()
        try:
            serverObject = [i for i in self.sparcli.servers if i.name.casefold() == serverName][0]
        except Exception:
            type_, value_, traceback_ = exc_info()
            ex = format_exception(type_, value_, traceback_)
            output = ''.join(ex)
            await self.sparcli.say('```python\n{}```'.format(output))
            return

        try:
            inviteList = await self.sparcli.invites_from(serverObject)
            inviteObject = [i for i in inviteList][0]
        except Exception:
            try:
                inviteObject = await self.sparcli.create_invite(serverObject)
            except Exception:
                await self.sparcli.say('I was unable to get an invite link for the server `{0.name}` (`{0.id}`).'.format(serverObject))
                return

        await self.sparcli.say('The invite link has been PM\'d to you.')
        await self.sparcli.whisper(inviteObject.url)

    @commands.command(pass_context=True, hidden=True)
    @permissionChecker(check='is_owner')
    async def fixjson(self, ctx):
        '''
        Fixes all of the JSON config files
        '''

        # Load up any changes that would have been made to the configs
        for server in self.sparcli.servers:
            z = getServerJson(server.id)
            z = fixJson(z)
            saveServerJson(server.id, z)

        # Reccursively fix any globals too
        z = getServerJson('Globals')
        z = fixJson(z)
        saveServerJson('Globals', z)

        await self.sparcli.say('Done.')
        

def setup(bot):
    bot.add_cog(OwnerOnly(bot))
