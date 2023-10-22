from commands import command, CommandError, Context
import lavalink
import discord
import re
import modules.music as m_mod
import logger
from lavalink.filters import LowPass


url_rx = re.compile(r'https?://(?:www\.)?.+')

def get_player(ctx: Context) -> lavalink.DefaultPlayer:
    return m_mod.lavaClient.player_manager.get(ctx.guild.id)

async def _ensure_voice(ctx: Context):
    """ This check ensures that the bot and command author are in the same voicechannel. """

    player: lavalink.PlayerManager = m_mod.lavaClient.player_manager.create(ctx.guild.id)
    # Create returns a player if one exists, otherwise creates.
    # This line is important because it ensures that a player always exists for a guild.

    # Most people might consider this a waste of resources for guilds that aren't playing, but this is
    # the easiest and simplest way of ensuring players are created.

    # These are commands that require the bot to join a voicechannel (i.e. initiating playback).
    # Commands such as volume/skip etc don't require the bot to be in a voicechannel so don't need listing here.
    should_connect = ctx.command.command in ('play',)

    if not ctx.author.voice or not ctx.author.voice.channel:
        # Our cog_command_error handler catches this and sends it to the voicechannel.
        # Exceptions allow us to "short-circuit" command invocation via checks so the
        # execution state of the command goes no further.
        if should_connect:
            raise CommandError('Join a voicechannel first.')

    v_client = ctx.voice_client
    if not v_client:
        if not should_connect:
            raise CommandError('Im not even playing...')
        permissions = ctx.author.voice.channel.permissions_for(ctx.guild.me)

        if not permissions.connect or not permissions.speak:  # Check user limit too?
            raise CommandError('I don\'t have permissions to join you :(')

        player.store('channel', ctx.channel.id)
        await ctx.author.voice.channel.connect(cls=m_mod.LavalinkVoiceClient, )
    else:
        if v_client.channel.id != ctx.author.voice.channel.id:
            raise CommandError('You need to be in my voicechannel.')


@command("play", aliases=['p'], pre_hook=_ensure_voice)
async def play(ctx: Context):
    """ Searches and plays a song from a given query. """
    player = get_player(ctx)
    query = ctx.command.rest.strip('<>')

    if not url_rx.match(query):
        query = f'ytsearch:{query}'

    results = await player.node.get_tracks(query)

    if not results or not results.tracks:
        return await ctx.channel.send('Nothing found!')

    embed = discord.Embed(color=discord.Color.blurple())

    # Valid loadTypes are:
    #   TRACK_LOADED    - single video/direct URL)
    #   PLAYLIST_LOADED - direct URL to playlist)
    #   SEARCH_RESULT   - query prefixed with either ytsearch: or scsearch:.
    #   NO_MATCHES      - query yielded no results
    #   LOAD_FAILED     - most likely, the video encountered an exception during loading.
    if results.load_type == 'PLAYLIST_LOADED':
        tracks = results.tracks

        for track in tracks:
            # Add all of the tracks from the playlist to the queue.
            player.add(requester=ctx.author.id, track=track)

        embed.title = 'Playlist Enqueued!'
        embed.description = f'{results.playlist_info.name} - {len(tracks)} tracks'
    else:
        track = results.tracks[0]
        embed.title = 'Track Enqueued'
        embed.description = f'[{track.title}]({track.uri})'

        player.add(requester=ctx.author.id, track=track)

    await ctx.channel.send(embed=embed)
    m_mod.channels.add_channel(ctx.message)
    # We don't want to call .play() if the player is playing as that will effectively skip
    # the current track.
    if not player.is_playing:
        await player.play()


@command("skip", aliases=['next'], pre_hook=_ensure_voice)
async def skip(ctx: Context):
    player = get_player(ctx)
    await ctx.reply(f"Skipping {player.current.title}")
    await player.skip()


@command("shuffle", pre_hook=_ensure_voice)
async def shuffle(ctx: Context):
    player = get_player(ctx)
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


@command("leave", aliases=['dc', 'disconnect'])
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
    channel = m_mod.channels.remove_channel(ctx.guild.id)
    # Disconnect from the voice channel.
    await ctx.voice_client.disconnect(force=True)
    await channel.send('Okay, I\'ll leave')
