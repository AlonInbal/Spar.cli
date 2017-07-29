from discord.ext import commands 
from Cogs.Utils.Exceptions import *


class ErrorManagement:

    def __init__(self, sparcli):
        self.sparcli = sparcli

    async def on_command_error(self, error, ctx):
        channel = ctx.message.channel
        server = ctx.message.server
        toSay = None

        if isinstance(error, BotPermissionsTooLow):
            # This should run if the bot doesn't have permissions to do a thing to a user
            toSay = 'That user is too high ranked for me to perform that action on them.'
            
        elif isinstance(error, MemberPermissionsTooLow):
            # This should run if the member calling a command doens't have permission to call it
            toSay = 'That user is too high ranked for you to run that command on them.'
            
        elif isinstance(error, MemberMissingPermissions):
            # This should be run should the member calling the command not be able to run it
            toSay = 'You are missing the permissions required to run that command.'

        elif isinstance(error, BotMissingPermissions):
            # This should be run if the bot can't run what it needs to
            toSay = 'I\'m missing the permissions required to run this command.'

        elif isinstance(error, DoesntWorkInPrivate):
            # This is to be run if the command is sent in PM
            toSay = 'This command does not work in PMs.'

        elif isinstance(error, ThisNeedsAToken):
            # The token was not provided for the command
            toSay = 'The bot owner has not set up the token for this command properly.'

        elif isinstance(error, CommandDisabled):
            # The command is disabled in the configs
            toSay = 'This command is disabled in the configuration for this server.'

        elif isinstance(error, commands.errors.MissingRequiredArgument):
            # Command was run improperly - missing arg
            toSay = 'Woah, it looks like you didn\'t run this command properly! Check out the help command to see how to use it.'

        elif isinstance(error, commands.errors.TooManyArguments):
            # Command was run improperly - extra arg
            toSay = 'Woah, it looks like you didn\'t run this command properly! Check out the help command to see how to use it.'

        elif isinstance(error, commands.errors.BadArgument):
            # Command was run improperly - improper arg
            toSay = 'Woah, it looks like you didn\'t run this command properly! Check out the help command to see how to use it.'
            
        elif isinstance(error, commands.errors.CheckFailure):
            # This should never really occur
            # This is if the command check fails
            toSay = 'Command check failed. Unknown error; please mention `Caleb#2831`.'
            
        else:
            # Who knows what happened? Not me. Raise the error again, and print to console
            print('Error on message :: Server{0.server.id} Author{0.author.id} Message{0.id} Content'.format(ctx.message), end='')
            try: print(ctx.message.content + '\n')
            except: print('Could not print.' + '\n')
            raise(error)

        await self.sparcli.send_message(channel, toSay)


def setup(bot):
    bot.add_cog(ErrorManagement(bot))
