from aiohttp import ClientSession 
from json import loads 
from collections import OrderedDict
from re import finditer
from discord.ext import commands 
from Cogs.Utils.Messages import makeEmbed


class Scriptures:

    def __init__(self, sparcli):
        self.sparcli = sparcli
        self.bible = 'https://getbible.net/json?scrip={}'
        self.biblePicture = 'http://pacificbible.com/wp/wp-content/uploads/2015/03/holy-bible.png'
        self.session = ClientSession(loop=sparcli.loop)

    def __unload(self):
        self.session.close()  

    async def getBiblePassage(self, passage):
        '''
        Goes through the getbible api to get a list of applicable Bible passages
        '''

        # Format the URL string
        toRetrieveFrom = self.bible.format(passage.replace(' ', '%20'))
        
        # Send the request to the site and return it as a JSON dictionary
        async with self.session.get(toRetrieveFrom) as r:
            text = await r.text()
        return loads(text[1:-2])


    @commands.command(pass_context=True, aliases=['christianity', 'bible'])
    async def christian(self, ctx, *, passage:str):
        '''
        Gets a passage from the Bible
        '''

        # TODO: MAKE ALL THIS CLEANER TO WORK WITH
        await self.sparcli.send_typing(ctx.message.channel)

        # Generate the string that'll be sent to the site
        getString = passage

        # Work out how many different quotes you need to get
        matches = finditer(r'[\d]+', passage)
        matchList = [i for i in matches]
        if len(matchList) == 2:
            passage = int(matchList[1].group())
            lastpassage = passage 
        elif len(matchList) == 3:
            passage = int(matchList[1].group())
            lastpassage = int(matchList[2].group())
        else:
            await self.sparcli.say('I was unable to get that passage.')
            return

        # Actually go get all the data from the site
        try:
            bibleData = await self.getBiblePassage(getString)
        except Exception:
            await self.sparcli.say('I was unable to get that passage.')
            return

        # Get the nice passages and stuff
        passageReadings = OrderedDict()
        chapterName = bibleData['book'][0]['book_name']
        chapterPassages = bibleData['book'][0]['chapter']
        chapterNumber = bibleData['book'][0]['chapter_nr']
        for i in range(passage, lastpassage + 1):
            passageReadings['{}:{}'.format(chapterNumber, i)] = chapterPassages[str(i)]['verse']

        # Make it into an embed
        em = makeEmbed(fields=passageReadings, author_icon=self.biblePicture, author=chapterName)

        # Boop it to the user
        await self.sparcli.say('', embed=em)


def setup(bot):
    bot.add_cog(Scriptures(bot))
