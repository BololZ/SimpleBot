import asyncio
import datetime

import discord
import yaml
from twitchAPI.twitch import Twitch

with open("config.yml", 'r') as stream:
    try:
        cfg = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)
chan_id = cfg['client']['chan_id']
chan_id_stream = cfg['twitch']['chan_id']
api_twitch_id = cfg['twitch']['client_id']
api_twitch_secret = cfg['twitch']['secret']
user_logins = cfg['twitch']['twitch_logins']


class MyClient(discord.AutoShardedClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # create the background task and run it in the background
        self.bg_task = self.loop.create_task(self.backgroung_task_chut())
        self.bg_task = self.loop.create_task(self.background_task_twitch())

    async def on_ready(self):
        print('Logged on as', self.user)
        print('Chan_id :', chan_id)

    async def backgroung_task_chut(self):
        await self.wait_until_ready()
        last_msg_id = 0
        while not self.is_closed():
            heure = datetime.datetime.now()
            h = str(heure.hour)
            m = str(heure.minute)
            print(h + ':' + m)
            if (int(h) >= 22 or int(h) <= 6) and (int(m) == 0):
                channel = self.get_channel(int(chan_id))
                next_msg_id = channel.last_message_id
                print('Last ID Msg :', last_msg_id)
                print('Next ID Msg :', next_msg_id)
                if last_msg_id != next_msg_id:
                    print('Chut.......<3')
                    await channel.send('Chut.....:heart:')
                    last_msg_id = channel.last_message_id
                del channel
            await asyncio.sleep(60)

    async def background_task_twitch(self):
        await self.wait_until_ready()
        # twitch_stream = dict()
        while not self.is_closed():
            twitch = Twitch(api_twitch_id, api_twitch_secret)
            try:
                twitch.authenticate_app([])
            except:
                print('Erreur auth Twitch')
            streamers = twitch.get_streams(user_login=user_logins)
            # channel = self.get_channel(int(chan_id_stream))
            # for stream in streamers:
            # print(stream)
            # username = stream[0]
            # print(username)
            # message = 'Maintenant en stream :heart: !!!!!\n**'
            # message += username
            # message += '**\n'
            # message += 'Titre : ***'
            # message += stream['title']
            # message += '***\n'
            # message += 'sur **'
            # message += game
            # message += '** pour **'
            # message += str(stream['viewer_count'])
            # message += '** viewers\n'
            # message += 'https://www.twitch.com/'
            # message += username.lower()
            # message += '\n'
            # message_markdown = markdown.markdown(message)
            # await channel.send(message)
            print(streamers)
            del streamers, twitch
            # del channel
            await asyncio.sleep(120)
