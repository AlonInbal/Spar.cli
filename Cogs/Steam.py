from aiohttp import ClientSession
from collections import OrderedDict
from random import choice
from re import finditer
from discord.ext import commands 
from Cogs.Utils.Messages import makeEmbed
from Cogs.Utils.Misc import htmlFixer


'''
Todo :: Add Steam game comparisons

* http://steamcommunity.com/id/USERID/games?tab=all&xml=1
* http://steamcommunity.com/profiles/USERID64/games?tab=all&xml=1
-- Both of those return XML of all games

* http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key=XXXXXXXXXXXXXXXXX&steamid=76561197960434622&format=json
-- Returns owned games of a player from an ID64 and API key
'''


class Steam:

    def __init__(self, sparcli):
        self.sparcli = sparcli
        self.gameInfo = 'http://store.steampowered.com/api/appdetails?appids={}&format=json'
        self.steamIcon = 'https://image.freepik.com/free-icon/steam-logo-games-website_318-40350.jpg'
        self.steamGames = [] # gameDict['applist']['apps']['app']
        self.session = ClientSession(loop=sparcli.loop)

    def __unload(self):
        self.session.close()

    def gameFinder(self, gameName:str):
        '''
        Returns a game ID as found from its name on the game list
        '''

        for i in self.steamGames:
            if gameName.lower() in i['name'].lower():
                return str(i['appid'])
        return None

    @commands.command(pass_context=True)
    async def steamsearch(self, ctx, *, gameName:str):
        '''
        Gets the information of a game from Steam
        '''

        await self.sparcli.send_typing(ctx.message.channel)

        # Populate the list if necessary
        if not self.steamGames:
            everyGame = 'http://api.steampowered.com/ISteamApps/GetAppList/v0001/'
            async with self.session.get(everyGame) as r:
                gameResp = await r.json()
            gameDict = gameResp
            self.steamGames = gameDict['applist']['apps']['app']

        # Try and get the game from the game list
        gameID = self.gameFinder(gameName)
        if gameID == None:
            await self.sparcli.say('I was unable to find the ID of that game on the Steam API.')
            return

        # Send it to the information formatter
        await self.getSteamGameInfo(gameID)

    @commands.command(pass_context=True)
    async def steamid(self, ctx, *, gameURL:str):
        '''
        Gets the information of a game from Steam URL
        '''

        await self.sparcli.send_typing(ctx.message.channel)

        # Grab the game ID from the user input
        regexMatches = finditer(r'\d+', gameURL)
        regexList = [i for i in regexMatches]

        # Parse it as a group
        if len(regexList) == 0:
            await self.sparcli.say('I was unable to find the ID of that game on the Steam API.')
            return
        else:
            await self.getSteamGameInfo(regexList[0].group())

    async def getSteamGameInfo(self, gameID:str=None):
        '''
        Gets the data of a game on Steam. Can only be done through ID
        '''

        # TODO: REDO THIS AS `dict.get(item, default)` SO AS TO MAKE IT CLEANER

        # Get the data from Steam
        async with self.session.get(self.gameInfo.format(gameID)) as r:
            steamData = await r.json()

        # Check to see if it was aquired properly
        if steamData[str(gameID)]['success'] == False:
            await self.sparcli.say('I was unable to find the ID of that game on the Steam API.')
            return

        # Get the embed information
        retData = OrderedDict()
        priceFormatter = lambda y, x: '{}{}.{}'.format(y, str(x)[:-2], str(x)[-2:]) if len(str(x)) > 2 else y + '0.' + str(x)
        gameData = steamData[gameID]['data']
        retData['Name'] = gameData['name']
        desc = gameData['short_description']
        desc = htmlFixer(desc)
        retData['Description'] = (desc, False)
        retData['Game ID'] = gameID
        try:
            m = gameData['metacritic']
            retData['Metacritic'] = '**{}**, [click here]({})'.format(m['score'], m['url'])
        except KeyError:
            pass
        retData['Categories'] = ', '.join([i['description'] for i in gameData['categories']])
        retData['Platforms'] = ', '.join([i.title() for i in list(gameData['platforms'].keys())])
        retData['Developer'] = ', '.join(gameData['developers'])
        retData['Publisher'] = ', '.join(gameData['publishers'])
        try:
            priceTemp = gameData['price_overview']
            if priceTemp['initial'] != priceTemp['final']:
                retData['Price'] = '~~{}~~ {}'.format(priceFormatter(priceTemp['currency'], priceTemp['initial']), priceFormatter(priceTemp['currency'], priceTemp['final']))
            else:
                retData['Price'] = priceFormatter(priceTemp['currency'], priceTemp['initial'])
        except KeyError:
            # The game is not released/does not have a price
            pass

        retData['Store Link'] = '[Open in Steam](steam://store/{0}/), [open in your browser](http://store.steampowered.com/app/{0}/)'.format(gameID)

        gameImage = choice(gameData['screenshots'])['path_full']

        # Delete stuff that doesn't exist
        for i, o in retData.items():
            if o == '':
                del retData[i]

        # Make it into an embed
        e = makeEmbed(author=retData['Name'], author_icon=self.steamIcon, colour=1, fields=retData, image=gameImage)

        # Return to user
        await self.sparcli.say('', embed=e)


def setup(bot):
    bot.add_cog(Steam(bot))
