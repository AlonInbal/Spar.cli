from aiohttp import get
from re import finditer
from random import choice
from collections import OrderedDict
from discord import Member
from discord.ext import commands
from Cogs.Utils.Configs import getTokens
from Cogs.Utils.Messages import makeEmbed

# Import translator
try:
    from microsofttranslator import Translator
    translatorImported = True
except ImportError:
    translatorImported = True

# Import WolframAlpha
try:
    from wolframalpha import Client
    wolframalphaImported = True
except ImportError:
    wolframalphaImported = False


class Internet:

    def __init__(self, sparcli):
        self.sparcli = sparcli
        self.urbanSite = 'https://api.urbandictionary.com/v0/define?term={}'
        self.translator = None
        self.wolfClient = None
        self.nounlist = []

        self.subredditCache = {}

        self.dogCache = None
        self.dogCacheTimeout = 10

        # Set up the translator, if you can
        if translatorImported != False:
            try:
                tokens = getTokens()
                secret = tokens['Microsoft Translate']['Secret']
                transid = tokens['Microsoft Translate']['ID']
                self.translator = Translator(transid, secret)
            except KeyError:
                pass

        # Set up Wolfram
        if wolframalphaImported == True:
            try:
                tokens = getTokens()
                secret = tokens['WolframAlpha']['Secret']
                self.wolfClient = Client(secret)
            except KeyError:
                pass

        # Set up noun list
        self.nounlist = [] # nounstr.split('\\n')

    @commands.command(pass_context=True)
    async def pun(self, ctx):
        '''
        Gives a random pun from the depths of the internet.
        '''

        # Send typing, so you can see it's being processed
        await self.sparcli.send_typing(ctx.message.channel)

        # Read from page
        async with get('http://www.punoftheday.com/cgi-bin/randompun.pl') as r:
            page = await r.text()

        # Scrape the raw HTML
        r = r'(<div class=\"dropshadow1\">\n<p>).*(</p>\n</div>)'
        foundPun = [i for i in finditer(r, page)][0].group()

        # Filter out the pun
        r = r'(>).*(<)'
        filteredPun = [i for i in finditer(r, foundPun)][0].group()

        # Boop it out
        fullPun = filteredPun[1:-1]
        await self.sparcli.say(fullPun)

    @commands.command(pass_context=True)
    async def trans(self, ctx, langTo: str, *, toChange: str):
        '''
        Translates from one language into another.
        '''

        # See if the translator has been logged into
        if self.translator == None:
            try:
                if translatorImported == False:
                    raise KeyError
                tokens = getTokens()
                secret = tokens['Microsoft Translate']['Secret']
                transid = tokens['Microsoft Translate']['ID']
                self.translator = Translator(transid, secret)
            except KeyError:
                await self.sparcli.say('Translation has not been set up for this bot.')
                return

        # Send typing, so you can see it's being processed
        await self.sparcli.send_typing(ctx.message.channel)

        # Make sure that the language is supported
        if langTo not in self.translator.get_languages():
            await self.sparcli.say("The language provided is not supported.")
            return

        # If so, translate it
        translatedText = self.translator.translate(toChange, langTo.lower())
        await self.sparcli.say(translatedText)

    @commands.command(pass_context=True)
    async def wolfram(self, ctx, *, toDo: str):
        '''
        Searches WolframAlpha for the given term. Returns text.
        '''

        # Call the internal search function
        await self.wolframSearch(ctx, toDo, False)

    @commands.command(pass_context=True)
    async def iwolfram(self, ctx, *, toDo: str):
        '''
        Searches WolframAlpha for the given term. Returns images.
        '''

        # Call the internal search function
        await self.wolframSearch(ctx, toDo, True)

    async def wolframSearch(self, ctx, whatToSearch, displayImages):
        '''
        Sends the actual search term to the Wolfram servers.
        '''

        # See if the Wolfram API has been loaded
        if self.wolfClient == None:
            try:
                if wolframalphaImported == False:
                    raise KeyError
                tokens = getTokens()
                secret = tokens['WolframAlpha']['Secret']
                self.wolfClient = Client(secret)
            except KeyError:
                await self.sparcli.say('WolframAlpha has not been set up for this bot.')
                return

        # Send typing, so you can see it's being processed
        await self.sparcli.send_typing(ctx.message.channel)

        # Sends query to Wolfram
        wolfResults = self.wolfClient.query(whatToSearch)

        # Set up a filter to remove Nonetype values
        removeNone = lambda x: [i for i in x if x != None]

        # Fix the results into a list - text or link
        if displayImages == False:
            u = '```\n{}```'
            wolfList = [u.format(i.text) for i in wolfResults.pods]
            wolfList = removeNone(wolfList)
        else:
            wolfList = [i.img for i in wolfResults.pods]

        # Return to user
        await self.sparcli.say(' '.join(wolfList[0:6]))

    @commands.command(pass_context=True)
    async def throw(self, ctx, *, member: Member=None):
        '''
        Throws a random thing at a user.
        '''

        # Populate list if necessary
        if not self.nounlist:
            nounSite = 'http://178.62.68.157/raw/nouns.txt'
            async with get(nounSite) as r:
                nounstr = await r.text()
            self.nounlist = nounstr.split('\n')

        # Get thrown object
        toThrow = choice(self.nounlist)
        aOrAn = 'an' if toThrow[0] in 'aeiou' else 'a'

        # See if the user is the bot
        if member == None:
            pass
        elif member.id == self.sparcli.user.id:
            await self.sparcli.say('Nice try.')
            return

        # Throw the object
        atUser = '.' if member == None else ' at {}.'.format(member.mention)
        await self.sparcli.say('Thrown {} {}{}'.format(aOrAn, toThrow, atUser))

    @commands.command(pass_context=True)
    async def urban(self, ctx, *, searchTerm:str):
        '''
        Allows you to search UrbanDictionary for a specific term.
        '''

        CHARACTER_LIMIT = 250

        # Make the url nice and safe
        searchTerm = searchTerm.replace(' ', '%20')
        async with get(self.urbanSite.format(searchTerm)) as r:
            siteData = await r.json()

        # Get the definitions
        definitionList = siteData['list']
        o = OrderedDict()
        counter = 0
        url = None

        if definitionList == []:
            await self.sparcli.say('No definitions found for the search term `{}`.'.format(searchTerm))
            return

        # Go through and get the definitions
        for definitionObject in definitionList:

            # Iterate the counter and setup some temp variables
            counter += 1
            author = definitionObject['author']
            definition = definitionObject['definition']

            # Cut off the end of too-long definitions
            if len(definition) > CHARACTER_LIMIT:
                deflist = []

                # Split it per word
                for q in definition.split(' '):

                    # Check if it's above the limit
                    if len(' '.join(deflist + [q])) > CHARACTER_LIMIT:
                        break 
                    else:
                        deflist.append(q)

                # Plonk some elipsies on the end
                definition = ' '.join(deflist) + '...'

            # Put it into the dictionary
            o['Definition #{} by {}'.format(counter, author)] = definition
            if counter == 3:
                break 

            # Get a working URL
            if url == None:
                v = definitionObject['permalink']
                url = '/'.join(v.split('/')[:-1])

        # Return to user
        em = makeEmbed(fields=o, author_url=url, author='Click here for UrbanDictionary', inline=False)
        await self.sparcli.say(embed=em)

    @commands.command(pass_context=True)
    async def xkcd(self, ctx, comicNumber:int='Latest'):
        '''
        Gets you an xkcd comic strip
        '''

        await self.sparcli.send_typing(ctx.message.channel)

        # Parse the comic input into a URL
        if comicNumber == 'Latest':
            comicURL = 'http://xkcd.com/info.0.json'
        else:
            comicURL = 'https://xkcd.com/{}/info.0.json'.format(comicNumber)

        async with get(comicURL) as r:
            try:
                data = await r.json()
            except Exception:
                await self.sparcli.say('Comic `{}` does not exist.'.format(comicNumber))
                return

        title = data['safe_title']
        alt = data['alt']
        image = data['img']
        number = data['num']
        url = 'https://xkcd.com/{}'.format(number)
        await self.sparcli.say(embed=makeEmbed(author=title, author_url=url, description=alt, image=image))


def setup(bot):
    bot.add_cog(Internet(bot))
