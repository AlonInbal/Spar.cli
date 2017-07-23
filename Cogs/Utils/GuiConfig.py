THUMBS = ['👍', '👎']


async def addEmojiList(message, emojiList):
    '''
    Adds a list of emoji to a message
    '''

    for i in emojiList:
        await message.add_reaction(message, i)


async def updateFromEmoji(sparcli, ctx, serverSettings, enableQuery, currentStatus):
    '''
    Configures a serverconfig depending on a given emoji
    '''

    # Shorten a line
    author = ctx.author

    # Print out message to user
    mes = await ctx.send('Enable {0}? (Presently `{1}`)'.format(enableQuery, currentStatus))

    # Add emoji to it
    await addEmojiList(mes, THUMBS)

    # See what the user gives back
    check = lambda r, u: r.emoji in THUMBS and u == author and r.message == mes
    r, _ = await sparcli.wait_for('reaction_add', check=check)

    # Set it up to save
    serverSettings['Toggles'][thingToEnable] = {'👍': True, '👎': False}[r.emoji]

    # Delete the message
    await mes.delete()

    return serverSettings


async def updateFromMessage(sparcli, ctx, serverSettings, thingToSet):
    '''Configures a serverconfig depending on a given message'''

    # Shorten a line
    author = ctx.author
    channel = ctx.channel
    limit = 0

    # Say out to user
    mes = [await sparcli.say('What channel should {0} be set to?'.format(thingToSet))]

    # Wait for response from user
    while True:
        ret = await sparcli.wait_for('message', author=author, channel=channel)

        # Check if there's a tagged channel
        mentioned = ret.channel_mentions
        if not mentioned:

            # There's not - up a counter
            limit += 1
            if limit == 5:
                await ctx.send('You\'ve failed this prompt too many times - aborting.')
                return None

            # Tell them they need to not be a lil shit
            z = await sparcli.say('You need to tag a channel in your message.')
            mes.append(z)
            mes.append(ret)

        else:

            # There's a tagged channel - delete the messages
            for q in mes + [ret]:
                await q.delete()

            # Save the settings
            serverSettings['Channels'][thingToSet] = mentioned[0].id

            # Exit the loop
            break

    return serverSettings
