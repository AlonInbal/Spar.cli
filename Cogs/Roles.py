from discord.ext import commands
from discord import Colour, Member, Permissions
from discord.errors import NotFound as Forbidden
from Cogs.Utils.Configs import getServerJson, saveServerJson
from Cogs.Utils.Messages import getTextRoles
from Cogs.Utils.Misc import colourFixer
from Cogs.Utils.Permissions import permissionChecker, botPermission


class RoleManagement:

    def __init__(self, sparcli):
        self.sparcli = sparcli

    @commands.command(pass_context=True, aliases=['changecolor', 'changerolecolour', 'changerolecolor'])
    @permissionChecker(check='manage_roles')
    @botPermission(check='manage_roles')
    async def changecolour(self, ctx, roleColour: str, *, roleName: str):
        '''
        Changes the colour of a specified role
        '''

        # Get the role colour
        roleColour = colourFixer(roleColour)

        # Get the role itself
        role = await getTextRoles(ctx, roleName, speak=True, sparcli=self.sparcli)
        if type(role) == int: return

        # Change the role colour
        colour = Colour(int(roleColour, 16))
        await self.sparcli.edit_role(ctx.message.server, role, colour=colour)
        await self.sparcli.say('The colour of the role `{0.name}` has been changed to value `{1.value}`.'.format(role, colour))

    @commands.command(pass_context=True)
    @botPermission(check='manage_roles', compare=True)
    async def iam(self, ctx, *, roleName: str):
        '''
        If allowed, the bot will give you a mentioned role
        '''

        if roleName == 'list':
            await self.iamlist(ctx)
            return

        connectedRoles = [i for i in ctx.message.server.roles if roleName.lower() in i.name.lower()]
        if len(connectedRoles) == 1:
            roleToGive = connectedRoles[0]
        elif len(connectedRoles) == 0:
            await self.sparcli.say('This server has no roles that match that hitstring.')
            return 
        else:
            await self.sparcli.say('This server has too many roles that match that hitstring.')
            return

        # See what you're allowed to self-assign
        serverSettings = getServerJson(ctx.message.server.id)
        allowableIDs = serverSettings['SelfAssignableRoles']

        # See if you can add that
        if roleToGive.id not in allowableIDs:
            await self.sparcli.say('You are not allowed to self-assign that role.')
            return

        # See if the user already has the role
        if roleToGive.id in [i.id for i in ctx.message.author.roles]:
            await self.sparcli.say('You already have that role.')
            return

        await self.sparcli.add_roles(ctx.message.author, roleToGive)
        await self.sparcli.say('The role `{0.name}` with ID `{0.id}` has been sucessfully added to you.'.format(roleToGive))

    async def iamlist(self, ctx):
        '''
        Gives a list of roles that you can self-assign
        '''

        # Get all the stuff on the server that you can give to yourself
        serverSettings = getServerJson(ctx.message.server.id)
        allowableIDs = serverSettings['SelfAssignableRoles']

        # Get their role names
        assignableRoles = [i.name for i in ctx.message.server.roles if i.id in allowableIDs]

        # There are no roles that you can add to yourself
        if len(assignableRoles) == 0:
            await self.sparcli.say('There are no self-assignable roles on this server.')
            return

        # Print back out the user
        await self.sparcli.say('The following roles are self-assignable: ```\n* {}```'.format('\n* '.join(assignableRoles)))

    @commands.group(pass_context=True)
    @permissionChecker(check='manage_roles')
    async def youare(self, ctx):
        pass

    @youare.command(pass_context=True, name='add', aliases=['now'])
    @permissionChecker(check='manage_roles')
    async def youareAdd(self, ctx, *, roleName:str):

        # Get the role itself
        roleToGive = await getTextRoles(ctx, roleName, speak=True, sparcli=self.sparcli)
        if type(roleToGive) == int: return

        # Read from the server configs
        serverSettings = getServerJson(ctx.message.server.id)
        allowableIDs = serverSettings['SelfAssignableRoles']

        if roleToGive.id not in allowableIDs:
            allowableIDs.append(roleToGive.id)
        else:
            await self.sparcli.say('This role can already be self-assigned.')
            return

        # Plonk the settings back into the file storage
        serverSettings['SelfAssignableRoles'] = allowableIDs
        saveServerJson(ctx.message.server.id, serverSettings)

        # Print out to the user
        await self.sparcli.say('The role `{0.name}` with ID `{0.id}` can now be self-assigned.'.format(roleToGive))

    @youare.command(pass_context=True, name='del', aliases=['not', 'delete'])
    @permissionChecker(check='manage_roles')
    async def youareDel(self, ctx, *, roleName:str):

        # Get the role itself
        roleToGive = await getTextRoles(ctx, roleName, speak=True, sparcli=self.sparcli)
        if type(roleToGive) == int: return

        # Read from the server configs
        serverSettings = getServerJson(ctx.message.server.id)
        allowableIDs = serverSettings['SelfAssignableRoles']

        if roleToGive.id in allowableIDs:
            allowableIDs.remove(roleToGive.id)
        else:
            await self.sparcli.say('This role cannot be self-assigned.')
            return

        # Plonk the settings back into the file storage
        serverSettings['SelfAssignableRoles'] = allowableIDs
        saveServerJson(ctx.message.server.id, serverSettings)

        # Print out to the user
        await self.sparcli.say('The role `{0.name}` with ID `{0.id}` can no longer be self-assigned.'.format(roleToGive))

    @commands.command(pass_context=True, aliases=['setcolor'])
    @permissionChecker(check='manage_roles')
    @botPermission(check='manage_roles')
    async def setcolour(self, ctx, colour:str, user:Member=None):
        '''
        Creates a new role with a given colour, and assigns it to a user
        '''

        # Fix up some variables
        server = ctx.message.server
        user = ctx.message.author if not user else user

        # Fix the colour string
        colour = colourFixer(colour)
        colourObj = Colour(int(colour, 16))
        # permissions=Permissions(permissions=0)

        # Find the role
        tempRoleFinder = [i for i in server.roles if user.id in i.name]
        if len(tempRoleFinder) > 0:
            role = tempRoleFinder[0]
            await self.sparcli.edit_role(server, role, colour=colourObj)
            created = False
        else:
            role = await self.sparcli.create_role(server, name='SPARCLI - {}'.format(user.id), colour=colourObj)
            await self.sparcli.add_roles(user, role)
            created = True

        # Print out to user
        await self.sparcli.say(
            'This role has been successfully {}. \n'
            'You may need to move the positions of other roles to make it work properly.'.format({True:'created',False:'edited'}[created])
        )


def setup(bot):
    bot.add_cog(RoleManagement(bot))
