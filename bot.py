import asyncio
import datetime
from typing import Optional, Any

import discord
from twitch import TwitchHelix
import yaml
#import markdown


with open("config.yml", 'r') as stream:
    try:
        cfg = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)
chan_id = cfg['client']['chan_id']
chan_id_stream = cfg['twitch']['chan_id']
api_twitch_id = cfg['twitch']['client_id']
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
            print(h+':'+m)
            if (int(h) >= 22 or int(h) <=5) and (int(m)%30 == 0):
                channel = self.get_channel(int(chan_id))
                next_msg_id = channel.last_message_id
                print('Last ID Msg :', last_msg_id)
                print('Next ID Msg :',next_msg_id)
                if last_msg_id != next_msg_id:
                    print('Chut.......<3')
                    await channel.send('Chut.....:heart:')
                    last_msg_id = channel.last_message_id
                del channel
            await asyncio.sleep(60)

    async def background_task_twitch(self):
        await self.wait_until_ready()
        twitch_stream = dict()
        channel = self.get_channel(int(chan_id_stream))
        while not self.is_closed():
            client = TwitchHelix(api_twitch_id)
            streamer = client.get_streams(user_logins=user_logins)
            for stream in streamer:
                if stream['type'] == 'live':
                    user_id = stream['user_id']
                    if twitch_stream.get(user_id) != stream['started_at']:
                        channel = self.get_channel(int(chan_id_stream))
                        twitch_stream[user_id] = stream['started_at']
                        game_data = client.get_games(stream['game_id'])
                        game = game_data[0]['name']
                        username = stream['user_name']
                        message = 'Maintenant en stream :heart: !!!!!\n**'
                        message += username
                        message += '**\n'
                        message += 'Titre : ***'
                        message += stream['title']
                        message += '***\n'
                        message += 'sur **'
                        message += game
                        message += '** pour **'
                        message += str(stream['viewer_count'])
                        message += '** viewers\n'
                        message += 'https://www.twitch.com/'
                        message += username.lower()
                        message += '\n'
                        #message_markdown = markdown.markdown(message)
                        await channel.send(message)
                        del channel
            del streamer, client
            await asyncio.sleep(120)
