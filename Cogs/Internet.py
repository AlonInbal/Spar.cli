from aiohttp import ClientSession, BasicAuth
from re import finditer
from random import choice
from collections import OrderedDict
from xml.etree import ElementTree as ET
from requests.auth import HTTPBasicAuth
from discord import Member
from discord.ext import commands
from Cogs.Utils.Configs import getTokens
from Cogs.Utils.Messages import makeEmbed
from Cogs.Utils.Misc import htmlFixer

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
        self.wolfClient = None
        self.nounlist = []

        self.subredditCache = {}

        self.dogCache = None
        self.dogCacheTimeout = 10

        # Set up Wolfram
        if wolframalphaImported == True:
            try:
                tokens = getTokens()
                secret = tokens['WolframAlpha']['Secret']
                self.wolfClient = Client(secret)
            except KeyError:
                pass

        # Set up noun list
        self.nounlist = [] 

        self.session = ClientSession(loop=sparcli.loop)

    def __unload(self):
        self.session.close()

    async def on_command(self, command, ctx):
        if command.cog_name == 'Internet':
            await self.sparcli.send_typing(ctx.message.channel)

    @commands.command(pass_context=True)
    async def pun(self, ctx):
        '''
        Gives a random pun from the depths of the internet
        '''

        # Read from page
        async with self.session.get('http://www.punoftheday.com/cgi-bin/randompun.pl') as r:
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
    async def wolfram(self, ctx, *, toDo: str):
        '''
        Searches WolframAlpha for the given term. Returns text
        '''

        # Call the internal search function
        await self.wolframSearch(ctx, toDo, False)

    @commands.command(pass_context=True)
    async def iwolfram(self, ctx, *, toDo: str):
        '''
        Searches WolframAlpha for the given term. Returns images
        '''

        # Call the internal search function
        await self.wolframSearch(ctx, toDo, True)

    async def wolframSearch(self, ctx, whatToSearch, displayImages):
        '''
        Sends the actual search term to the Wolfram servers
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
        Throws a random thing at a user
        '''

        # Populate list if necessary
        if not self.nounlist:
            nounSite = 'http://178.62.68.157/raw/nouns.txt'
            async with self.session.get(nounSite) as r:
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
        Allows you to search UrbanDictionary for a specific term
        '''

        CHARACTER_LIMIT = 250

        # Make the url nice and safe
        searchTerm = searchTerm.replace(' ', '%20')
        async with self.session.get(self.urbanSite.format(searchTerm)) as r:
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

        # Parse the comic input into a URL
        if comicNumber == 'Latest':
            comicURL = 'http://xkcd.com/info.0.json'
        else:
            comicURL = 'https://xkcd.com/{}/info.0.json'.format(comicNumber)

        async with self.session.get(comicURL) as r:
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

    @commands.command(pass_context=True)
    async def currency(self, ctx, base:str, amount:str, target:str):
        '''
        Converts from one currency to another
        '''

        try:
            float(amount)
        except ValueError:
            try:
                float(base)
                b = base 
                base = amount
                amount = b
            except ValueError:
                await self.sparcli.say('Please provide an amount to convert.')
                return

        base = base.upper(); target = target.upper()
        url = 'http://api.fixer.io/latest?base={0}&symbols={0},{1}'.format(base, target)
        async with self.session.get(url) as r:
            data = await r.json()

        # Format the data into something useful
        if len(data['rates']) < 1:
            await self.sparcli.say('One or both of those currency targets aren\'t supported.')
            return 

        # Get an output
        o = OrderedDict()
        o['Base'] = base 
        o['Target'] = target 
        o['Exchange Rate'] = '1:%.2f' %data['rates'][target]
        v = float(data['rates'][target]) * float(amount)
        o['Exchanged Price'] = '{}{} = {}{}'.format(base, amount, target, '%.2f' %v)
        e = makeEmbed(fields=o)
        await self.sparcli.say(embed=e)

    @commands.command(pass_context=True)
    async def netflix(self, ctx, *, showName:str):
        '''
        Gives you the details of a show on Netflix
        '''

        url = 'http://netflixroulette.net/api/api.php?title=' + showName
        async with self.session.get(url) as r:
            resp = r.status
            data = await r.json()

        if resp == 404:
            await self.sparcli.say('The show with the title `{}` could not be found.'.format(showName.title()))
            return

        # Process the data
        o = OrderedDict()
        o['Summary'] = (data.get('summary'), False)
        o['Release Year'] = data.get('release_year')
        o['Rating'] = data.get('rating')
        o['Runtime'] = data.get('runtime')
        o['Category'] = data.get('category')
        o['Link'] = '[Click here](https://www.netflix.com/title/{})'.format(data.get('show_id'))
        o['ID'] = data.get('show_id')
        e = makeEmbed(author=data.get('show_title'), image=data.get('poster'), fields=o)
        await self.sparcli.say(embed=e)

    @commands.command(pass_context=True)
    async def anime(self, ctx, *, animeName:str):
        '''
        Gives you the details of an anime
        '''

        # Make sure there are the correct tokens in the bot
        tokens = getTokens()
        userPass = tokens['MyAnimeList']
        if '' in userPass.values():
            await self.sparcli.say('The command has not been set up to work on this bot.')
            return

        # Authenticate
        auth = BasicAuth(userPass['Username'], userPass['Password'])
        url = 'https://myanimelist.net/api/anime/search.xml?q=' + animeName.replace(' ', '+')

        # Send the request
        async with self.session.get(url, auth=auth) as r:
            resp = r.status
            data = await r.text()

        # Make sure everything's alright
        if resp == 204:
            await self.sparcli.say('The anime with the title `{}` could not be found.'.format(animeName.title()))
            return
        elif resp == 200:
            pass
        else:
            await self.sparcli.say('There was an error with this bot\'s authentication details.')
            return

        # Parse the XML data
        root = ET.fromstring(data)
        anime = root[0]
        o = OrderedDict()

        # Plonk it into an embed
        v = htmlFixer(anime[10].text)
        v = v if len(v) < 1000 else v[:1000]
        while v[-1] in ' .,?;\'"/!':
            v = v[:-1]
        v = v + '...'
        o['Summary'] = (v, False)
        o['Episodes'] = anime[4].text
        o['Rating'] = anime[5].text + '/10.00'
        o['Media Type'] = anime[6].text
        o['Status'] = anime[7].text
        image = anime[11].text
        title = anime[1].text

        # Echo out to the user
        e = makeEmbed(author=title, image=image, fields=o)
        await self.sparcli.say(embed=e)

    @commands.command(pass_context=True, aliases=['df'])
    async def define(self, ctx, *, wordToDefine:str):
        '''
        Defines a word using the Oxford Dictionary
        '''

        wordToDefine = wordToDefine.lower()

        # Make sure there are the correct tokens in the bot
        tokens = getTokens()
        userPass = tokens['OxfordDictionary']
        if '' in userPass.values():
            await self.sparcli.say('The command has not been set up to work on this bot.')
            return

        # Send a request to the server
        base = 'https://od-api.oxforddictionaries.com/api/v1/entries/en/{}/definitions'
        url = base.format(wordToDefine)
        headers = {'app_id': userPass['ID'], 'app_key': userPass['Key']}
        async with self.session.get(url, headers=headers) as r:
            resp = r.status 
            if resp == 404:
                pass
            else:
                data = await r.json()

        # Make sure there was a valid response
        if resp == 404:
            await self.sparcli.say('There were no definitions for the word `{}`.'.format(wordToDefine))
            return

        # Format the data into an embed
        a = data['results']
        b = a[0]
        c = b['lexicalEntries']
        d = c[0]
        e = d['entries']
        f = e[0]
        g = f['senses']
        definitions = [i['definitions'][0] for i in g]

        o = OrderedDict()
        for i, p in enumerate(definitions):
            o['Definition #{}'.format(i+1)] = p 

        e = makeEmbed(author='Definition of {}'.format(wordToDefine), fields=o, inline=False)
        await self.sparcli.say(embed=e)


def setup(bot):
    bot.add_cog(Internet(bot))
