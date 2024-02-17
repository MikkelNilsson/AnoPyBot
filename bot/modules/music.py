import discord
import lavalink
import logger
import os
from schema import Context, CommandError

lavaClient: lavalink.Client = None

def get_player(ctx: Context) -> lavalink.DefaultPlayer:
    return lavaClient.player_manager.get(ctx.guild.id)

async def ensure_voice(ctx: Context):
    """ This check ensures that the bot and command author are in the same voicechannel. """

    player: lavalink.PlayerManager = lavaClient.player_manager.create(ctx.guild.id)
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
        await ctx.author.voice.channel.connect(cls=LavalinkVoiceClient)
    else:
        if v_client.channel.id != ctx.author.voice.channel.id:
            raise CommandError('You need to be in my voicechannel.')


class LavalinkVoiceClient(discord.VoiceClient):
    """
    This is the preferred way to handle external voice sending
    This client will be created via a cls in the connect method of the channel
    see the following documentation:
    https://discordpy.readthedocs.io/en/latest/api.html#voiceprotocol
    """

    def __init__(self, client: discord.Client, channel: discord.abc.Connectable):
        self.client = client
        self.channel = channel
        # ensure a client already exists
        if not lavaClient:
            raise RuntimeError("Lavalink client is not set up");


    async def on_voice_server_update(self, data):
        # the data needs to be transformed before being handed down to
        # voice_update_handler
        lavalink_data = {
            't': 'VOICE_SERVER_UPDATE',
            'd': data
        }
        await lavaClient.voice_update_handler(lavalink_data)

    async def on_voice_state_update(self, data):
        # the data needs to be transformed before being handed down to
        # voice_update_handler
        lavalink_data = {
            't': 'VOICE_STATE_UPDATE',
            'd': data
        }
        await lavaClient.voice_update_handler(lavalink_data)

    async def connect(self, *, timeout: float, reconnect: bool, self_deaf: bool = False, self_mute: bool = False) -> None:
        """
        Connect the bot to the voice channel and create a player_manager
        if it doesn't exist yet.
        """
        # ensure there is a player_manager when creating a new voice_client
        lavaClient.player_manager.create(guild_id=self.channel.guild.id)
        await self.channel.guild.change_voice_state(channel=self.channel, self_mute=self_mute, self_deaf=self_deaf)

    async def disconnect(self, *, force: bool = False) -> None:
        """
        Handles the disconnect.
        Cleans up running player and leaves the voice client.
        """
        player = lavaClient.player_manager.get(self.channel.guild.id)

        # no need to disconnect if we are not connected
        if not force and not player.is_connected:
            return

        # None means disconnect
        await self.channel.guild.change_voice_state(channel=None)

        # update the channel_id of the player to None
        # this must be done because the on_voice_state_update that would set channel_id
        # to None doesn't get dispatched after the disconnect
        player.channel_id = None
        self.cleanup()

# Hooks
class Lava_Hook:
    def __init__(self, client: discord.Client) -> None:
        self.bot = client
        global lavaClient
        lavaClient.add_event_hook(self.event_hook)

    async def event_hook(self, event: lavalink.events.Event):
        if isinstance(event, lavalink.events.QueueEndEvent):
            await self.queue_end(event)
        elif isinstance(event, lavalink.events.TrackStartEvent):
            await self.track_start(event)


    async def queue_end(self, event: lavalink.events.QueueEndEvent):
        guild_id = event.player.guild_id
        guild = self.bot.get_guild(guild_id)
        # This is not a text channel
        await channels.get_channel(guild_id).send('I have no more music to play...')
        await guild.voice_client.disconnect(force=True)

    async def track_start(self, event: lavalink.events.TrackStartEvent):
        await channels.get_channel(event.player.guild_id).send(
            'Now playing: ' + event.track.title + '\n' + event.track.uri
        )


class MusicTextChannel():
    channels: dict[int, discord.TextChannel]

    def __init__(self):
        self.channels = dict()

    def add_channel(self, message: discord.Message) -> None:
        self.channels[message.guild.id] = message.channel

    def get_channel(self, guild_id: int) -> discord.TextChannel:
        if guild_id in self.channels:
            return self.channels[guild_id]
        else:
            RuntimeError(f"No music channel for {guild_id}")

    def remove_channel(self, guild_id: int) -> discord.TextChannel:
        res = self.channels[guild_id]
        del self.channels[guild_id]
        return res

channels: MusicTextChannel = None

def setup(client: discord.Client):
    global lavaClient
    lavaClient = lavalink.Client(client.user.id)
    lavaClient.add_node(
        'lavalink',
        int(os.getenv("LAVALINK_PORT", 2333)),
        os.getenv("LAVALINK_PASSWORD", 'youshallnotpass'),
        'eu',
        'default-node'
    )
    global channels
    channels = MusicTextChannel()
    Lava_Hook(client)