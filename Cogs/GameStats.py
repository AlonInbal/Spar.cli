from aiohttp import ClientSession
from collections import OrderedDict
from datetime import timedelta
from discord.ext import commands
from Cogs.Utils.Messages import makeEmbed


class GameStats(object):

    def __init__(self, sparcli):
        self.sparcli = sparcli
        self.session = ClientSession(loop=sparcli.loop)

    def __unload(self):
        self.session.close()  

    @commands.command(pass_context=True, aliases=['poke', 'pkmn'])
    async def pokemon(self, ctx, *, pokemonName:str):
        '''
        Gives you information on a given Pokemon
        '''

        await self.sparcli.send_typing(ctx.message.channel)
        pokeSite = 'http://pokeapi.co/api/v2/pokemon/{}'.format(pokemonName)
        typeColours = {
            'Normal': 11052922, 
            'Fire': 15630640, 
            'Water': 6525168, 
            'Electric': 16240684, 
            'Grass': 8046412, 
            'Ice': 9886166, 
            'Fighting': 12725800, 
            'Poison': 10698401, 
            'Ground': 14860133, 
            'Flying': 11112435, 
            'Psychic': 16340359, 
            'Bug': 10926362, 
            'Rock': 11968822, 
            'Ghost': 7559063, 
            'Dragon': 7288316, 
            'Dark': 7362374, 
            'Steel': 12040142, 
            'Fairy': 14058925
        }

        async with self.session.get(pokeSite) as r:
            data = await r.json()

        if data.get('detail', False):
            await self.sparcli.say('That Pokémon could not be found.')
            return

        # Format the information nicely
        o = OrderedDict()
        pokemonName = data['name'].title()
        o['Pokédex Number'] = data['id']
        o['Types'] = ', '.join([i['type']['name'].title() for i in data['types']])
        colour = typeColours.get(data['types'][0]['type']['name'].title(), 0)
        o['Abilities'] = ', '.join([i['ability']['name'].replace('-', ' ').title() for i in data['abilities']])
        o['Height'] = '{}m'.format(data['height']/10.0)
        o['Weight'] = '{}kg'.format(data['weight']/10.0)
        image = 'https://img.pokemondb.net/artwork/{}.jpg'.format(pokemonName.lower())
        e = makeEmbed(author=pokemonName, colour=colour, fields=o, image=image)
        await self.sparcli.say('', embed=e)

    @commands.command(pass_context=True, aliases=['ow'])
    async def overwatch(self, ctx, *, battleTag:str, playType:str='quickplay'):
        '''
        Gives you an overview of some Overwatch stats for the PC
        '''

        playType = battleTag.split(' ')[-1]
        battleTag = battleTag.split(' ')[0]
        if playType == battleTag:
            playType = 'quickplay'
        if playType.lower() in ['comp', 'competitive', 'compet', 'c', 'com', 'competitivity']:
            playType = 'competitive'
        else:
            playType = 'quickplay'
        await self.overwatchStats(ctx, battleTag, 'pc', playType)

    @commands.command(pass_context=True)
    async def overwatchps4(self, ctx, *, battleTag:str, playType:str='quickplay'):
        '''
        Gives you an overview of some Overwatch stats for PSN
        '''
        
        playType = battleTag.split(' ')[-1]
        battleTag = battleTag.split(' ')[0]
        if playType == battleTag:
            playType = 'quickplay'
        if playType.lower() in ['comp', 'competitive', 'compet', 'c', 'com', 'competitivity']:
            playType = 'competitive'
        else:
            playType = 'quickplay'
        await self.overwatchStats(ctx, battleTag, 'psn', playType)

    async def overwatchStats(self, ctx, battleTag, platform, playType):

        await self.sparcli.send_typing(ctx.message.channel)

        # Get the data from the server
        url = 'https://owapi.net/api/v3/u/{}/blob?platform={}'.format(battleTag.replace('#', '-'), platform)
        async with self.session.get(url, headers={'User-Agent': 'Discord bot Sparcli by Caleb#2831'}) as r:
            if str(r.status)[0] == '5':
                await self.sparcli.say('Oh. The service for this API is down. Sorry. Try again later, maybe?')
                return
            elif str(r.status)[0] == '4':
                await self.sparcli.say('That resource could not be found on the server.')
                return
            data = await r.json()

        # Determine which server to read from
        tempDat = [data.get('us', {}), data.get('eu', {}), data.get('kr', {}), data.get('any', {})]
        adata = None
        for i in tempDat:

            # Set a default
            if adata == None: adata = i 

            # Try - catch for keyerror
            try:

                # Determine their level
                l = i['stats']['quickplay']['overall_stats']
                maxLev = (l.get('prestige', 0) * 100) + l.get('level', 0)

                # Determine the stored's level
                try:
                    k = adata['stats']['quickplay']['overall_stats']
                    compLev = (k.get('prestige', 0) * 100) + k.get('level', 0)
                except (KeyError, TypeError):
                    compLev = -10

                # Restore the server with the largest level
                if maxLev > compLev:
                    adata = i 

            # Keyerror in comparison
            except (KeyError, TypeError):
                pass

        # Set this up for quick usage
        data = adata['stats'][playType]

        # Get the relevant data from the retrieved stuff
        o = OrderedDict()
        t = data['overall_stats']  # Temp variable
        avatar = t.get('avatar')
        o['Overall Stats'] = '{wins} wins vs {losses} losses over {games} games ({winrate}% win rate)'.format(
            wins=t.get('wins'),
            losses=t.get('losses'),
            games=t.get('games'),
            winrate=t.get('win_rate')
        )
        o['Rank'] = 'N/A' if not t.get('tier', 0) else t.get('tier').title()
        o['Level'] = '{}'.format(int((t.get('prestige') * 100) + t.get('level')))
        o['SR'] = 'N/A' if not t.get('comprank', 0) else int(t.get('comprank'))

        t = adata['heroes']['playtime'][playType]
        v = []
        b = []
        for y, u in t.items():
            v.append(y)
            b.append(u)
        mostUsed = v[b.index(max(b))]
        maxTime = timedelta(hours=max(b))
        o['Most Used Hero'] = '{} ({})'.format(mostUsed.title(), str(maxTime))

        t = data['game_stats']
        o['Total Eliminations'] = 'N/A' if not t.get('eliminations', 0) else int(t.get('eliminations'))
        o['Total Deaths'] = 'N/A' if not t.get('deaths', 0) else int(t.get('deaths'))

        o['Total Solo Kills'] = 'N/A' if not t.get('solo_kills', 0) else int(t.get('solo_kills'))
        o['Total Final Blows'] = 'N/A' if not t.get('final_blows', 0) else int(t.get('final_blows'))
        o['Total Damage Done'] = 'N/A' if not t.get('damage_done', 0) else int(t.get('damage_done'))
        o['Total Healing Done'] = 'N/A' if not t.get('healing_done', 0) else int(t.get('healing_done'))

        o['Most Solo Kills in Game'] = 'N/A' if not t.get('solo_kills_most_in_game', 0) else int(t.get('solo_kills_most_in_game'))
        o['Most Final Blows in Game'] = 'N/A' if not t.get('final_blows_most_in_game', 0) else int(t.get('final_blows_most_in_game'))
        o['Most Damage Done in Game'] = 'N/A' if not t.get('damage_done_most_in_game', 0) else int(t.get('damage_done_most_in_game'))
        o['Most Healing Done in Game'] = 'N/A' if not t.get('healing_done_most_in_game', 0) else int(t.get('healing_done_most_in_game'))

        o['Best Killstreak in Game'] = 'N/A' if not t.get('kill_streak_best', 0) else int(t.get('kill_streak_best'))

        # Format into an embed
        e = makeEmbed(author='{} Overwatch Stats for {}'.format(playType.title(), battleTag), fields=o, author_icon=avatar)
        await self.sparcli.say('', embed=e)


def setup(bot):
    bot.add_cog(GameStats(bot))
