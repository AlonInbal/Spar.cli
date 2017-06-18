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
        self.quranPicture = 'http://www.siotw.org/modules/burnaquran/images/quran.gif'
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

    async def getQuranPassage(self, passage):
        '''Goes through the alquran api to get quran passages'''
        bible = 'http://api.alquran.cloud/ayah/{}/en.sahih'
        toRetrieveFrom = bible.format(passage)
        # data = get(toRetrieveFrom).content
        async with self.session.get(toRetrieveFrom) as r:
            data = await r.json()
        return data


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

    @commands.command(pass_context=True)
    async def quran(self, ctx, *, passage: str):
        '''
        Gets a passage from the Quran
        '''

        await self.sparcli.send_typing(ctx.message.channel)

        # Generate the string that'll be sent to the site
        getString = passage

        # Work out how many different quotes you need to get
        tempPass = passage.split(':')[1]  # Gets the 34-35 from 14:34-35
        if len(tempPass.split('-')) == 2:
            passage = int(tempPass.split('-')[0])
            lastpassage = int(tempPass.split('-')[1])
        else:
            passage = lastpassage = int(tempPass)

        # Actually go get all the data from the site
        bibleData = await self.getQuranPassage(getString)

        # Get the nice passages and stuff
        passageReadings = OrderedDict()
        chapterName = bibleData['data']['surah']['englishName']
        chapterPassages = bibleData['data']
        chapterNumber = bibleData['data']['surah']['number']
        for i in range(passage, lastpassage + 1):
            getThisTurn = '{}:{}'.format(chapterNumber, i)
            bibleData = await self.getQuranPassage(getThisTurn)
            y = bibleData['data']['text']
            passageReadings[getThisTurn] = y

        # Make it into an embed
        em = makeEmbed(
            fields=passageReadings,
           author_icon=self.quranPicture, 
           author=chapterName, 
           colour=0x258D58
        )

        # Boop it to the user
        await self.sparcli.say('', embed=em)


def setup(bot):
    bot.add_cog(Scriptures(bot))
