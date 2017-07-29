from random import randint
from time import strftime
from re import finditer
from discord import Embed
from discord.ext import commands


async def getTextRoles(ctx, hitString, speak=False):
    '''
    Gets non-tagged and tagged roles from a message's ctx
    '''

    # Go through the guild roles
    guildRoles = ctx.guild.roles 
    hits = [i for i in guildRoles if hitString.lower() in i.name.lower()]
    if len(hits) == 1:
        return hits[0]

    if speak:
        await ctx.send('There were `{}` hits for that string within this guild\'s roles.'.format(len(hits)))
    return len(hits)


def makeEmbed(**kwargs):
    '''
    Creates an embed messasge with specified inputs.
    Parameters
    ----------
        author
        author_url
        author_icon
        user
        colour
        fields
        inline
        thumbnail
        image
        footer
        footer_icon
    '''

    # Get the attributes from the user
    Empty = Embed.Empty
    if True:

        # Get the author/title information
        author = kwargs.get('author', Empty)
        author_url = kwargs.get('author_url', Empty)
        author_icon = kwargs.get('author_icon', Empty)
        user = kwargs.get('user', None)

        # Get the colour
        colour = kwargs.get('colour', 0)

        # Get the values
        fields = kwargs.get('fields', {})
        inline = kwargs.get('inline', True)
        description = kwargs.get('description', Empty)

        # Images
        thumbnail = kwargs.get('thumbnail', False)
        image = kwargs.get('image', False)

        # Footer
        footer = kwargs.get('footer', Empty)
        footer_icon = kwargs.get('footer_icon', Empty)

    if footer == Empty:
        v = randint(0, 20)
        if v == 0:
            footer = 'Support me at https://patreon.com/CallumBartlett c:'
        elif v == 1:
            footer = 'Use the `invite` command to add me to your own server!'
    elif footer == None:
        footer = Empty

    # Filter the colour into a usable form
    # This may not work any more on the rewrite
    if type(colour).__name__ == 'Message':
        colour = colour.author.colour.value
    elif type(colour).__name__ == 'Guild':
        colour = colour.me.colour.value 
    elif type(colour).__name__ == 'Member':
        colour = colour.colour.value

    # Correct the icon and author with the member, if necessary
    if user != None:
        author = user.display_name if author == Empty else author
        author_icon = user.avatar_url
        try:
            colour = user.colour.value if colour == 0 else colour
        except AttributeError:
            pass

    # Create an embed object with the specified colour
    embedObject = Embed(colour=colour)

    # Set the normal attributes
    if author != Empty:
        embedObject.set_author(name=author, url=author_url, icon_url=author_icon)
    embedObject.set_footer(text=footer, icon_url=footer_icon)
    embedObject.description = description
    
    # Set the attributes that have no default
    if image: 
        embedObject.set_image(url=image)
    if thumbnail: 
        embedObject.set_thumbnail(url=thumbnail)

    # Set the fields
    for i, o in fields.items():

        # Default inline
        p = inline

        # Check for custom inline
        if type(o) in [tuple, list]:
            p = o[1]
            o = o[0]

        # Add field
        embedObject.add_field(name=i, value=o, inline=p)

    # Return to user
    return embedObject


def messageToEmbed(message):

    # Get some default values that'll be in the embed
    author = message.author 
    description = message.content
    image = False

    # Check to see if any images were added
    regexMatch = r'.+(.png)|.+(.jpg)|.+(.jpeg)|.+(.gif)'
    if len(message.attachments) > 0:
        attachment = message.attachments[0]  # We can only get one attachment sorry ♥
        matchList = [i for i in finditer(regexMatch, attachment['filename'])]
        if len(matchList) > 0:
            image = attachment['url']

    # Get the time the message was created
    createdTime = '.'.join(str(message.created_at).split('.')[:-1])

    # Make and return the embed
    return makeEmbed(user=author, description=description, image=image, footer=createdTime)
