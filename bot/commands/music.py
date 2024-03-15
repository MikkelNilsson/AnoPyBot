from commands import command, Context, CommandError
import lavalink
import discord
import re
import modules.music as m_mod
import logger
from lavalink.filters import LowPass
from lavalink.server import LoadType
from schema import CommandModule


url_rx = re.compile(r'https?://(?:www\.)?.+')

@command(
    "Play",
    modules=[CommandModule.MUSIC],
    aliases=['p'],
    pre_hook=m_mod.ensure_voice,
    usage="play phrase_or_link",
    description="playes music for a voicechannel. Play from youtube or soundcloud."
)
async def play(ctx: Context):
    """ Searches and plays a song from a given query. """
    player = m_mod.get_player(ctx)
    query = ctx.command.rest.strip('<>')

    if not url_rx.match(query):
        query = f'ytsearch:{query}'

    results = await player.node.get_tracks(query)

    embed = discord.Embed(color=discord.Color.from_rgb(255, 255, 255))
    logger.info(results.load_type)
    if results.load_type == LoadType.PLAYLIST:
        tracks = results.tracks

        for track in tracks:
            # Add all of the tracks from the playlist to the queue.
            player.add(requester=ctx.author.id, track=track)

        embed.title = 'Playlist Enqueued!'
        embed.description = f'{results.playlist_info.name} - {len(tracks)} tracks'
    elif results.load_type in [LoadType.TRACK, LoadType.SEARCH]:
        track = results.tracks[0]
        embed.title = 'Track Enqueued'
        embed.description = f'[{track.title}]({track.uri})'

        player.add(requester=ctx.author.id, track=track)
    else:
        log_msg = ""
        if results.load_type == LoadType.EMPTY:
            msg = "No songs found. Try changing the search phrase."
        elif results.load_type == LoadType.ERROR:
            msg = "An error occured :("
            log_msg = results.error.cause
        raise CommandError(msg, log=(f"Error occured: {log_msg}" if log_msg else None))

    await ctx.channel.send(embed=embed)
    # We don't want to call .play() if the player is playing as that will effectively skip
    # the current track.
    if not player.is_playing:
        await player.play()


@command(
    "Skip",
    modules=[CommandModule.MUSIC],
    aliases=['Next'],
    pre_hook=m_mod.ensure_voice,
    description="Skips the current song."
)
async def skip(ctx: Context):
    player = m_mod.get_player(ctx)
    await ctx.reply(f"Skipping {player.current.title}")
    await player.skip()


@command(
    "Shuffle",
    modules=[CommandModule.MUSIC],
    pre_hook=m_mod.ensure_voice,
    description="Shuffles the queue. Note, it's a toggle, so to ushuffle repeat the command."
)
async def shuffle(ctx: Context):
    player = m_mod.get_player(ctx)
    player.shuffle = not player.shuffle
    if player.shuffle:
        await ctx.reply("Queue is been shuffled, repeat the command to unshuffle")
    else:
        await ctx.reply("Queue is not being shuffled anymore")


# @command("lowpass", aliases=['lp'], pre_hook=_ensure_voice)
# async def lowpass(ctx: Context):
#     """ Sets the strength of the low pass filter. """
#     # Get the player for this guild from cache.
#     player = m_mod.lavaClient.player_manager.get(ctx.guild.id)

#     if not ctx.command.args or len(ctx.command.args) < 0:
#         raise CommandError("Lowpass needs a value!")

#     strength = float(ctx.command.args[0])

#     strength = max(0.0, strength)
#     strength = min(100, strength)

#     embed = discord.Embed(color=discord.Color.blurple(), title='Low Pass Filter')

#     # A strength of 0 effectively means this filter won't function, so we can disable it.
#     if strength == 0.0:
#         await player.remove_filter('lowpass')
#         embed.description = 'Disabled **Low Pass Filter**'
#         return await ctx.channel.send(embed=embed)

#     # Lets create our filter.
#     low_pass = LowPass()
#     low_pass.update(smoothing=strength)

#     await player.set_filter(low_pass)

#     embed.description = f'Set **Low Pass Filter** strength to {strength}.'
#     await ctx.channel.send(embed=embed)


@command(
    "Leave",
    modules=[CommandModule.MUSIC],
    aliases=['dc', 'disconnect'],
    pre_hook=m_mod.ensure_voice,
    description="The bot disconnects from the voicechannel."
)
async def disconnect(ctx: Context):
    """ Disconnects the player from the voice channel and clears its queue. """
    player = m_mod.lavaClient.player_manager.get(ctx.guild.id)

    if not ctx.voice_client:
        return await ctx.channel.send('WTF! I\'m not even playing!')

    if not ctx.author.voice or (player.is_connected and ctx.author.voice.channel.id != int(player.channel_id)):
        return await ctx.channel.send('Why? You\'re not even in my voicechannel!')

    # Clear the queue to ensure old tracks don't start playing
    # when someone else queues something.
    player.queue.clear()
    # Stop the current track so Lavalink consumes less resources.
    await player.stop()

    # Disconnect from the voice channel.
    await ctx.voice_client.disconnect(force=True)
    await ctx.channel.send('Okay, I\'ll leave')
