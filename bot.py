import asyncio
from datetime import datetime

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
        # self.bg_task = self.loop.create_task(self.backgroung_task_chut())
        self.bg_task = self.loop.create_task(self.background_task_twitch())

    async def on_ready(self):
        print('Logged on as', self.user)
        print('Chan_id :', chan_id)

    # async def backgroung_task_chut(self):
    #     await self.wait_until_ready()
    #     last_msg_id = 0
    #     while not self.is_closed():
    #         heure = datetime.datetime.now()
    #         h = str(heure.hour)
    #         m = str(heure.minute)
    #         print(h + ':' + m)
    #         if (int(h) >= 22 or int(h) <= 6) and (int(m) == 0):
    #             channel = self.get_channel(int(chan_id))
    #             next_msg_id = channel.last_message_id
    #             print('Last ID Msg :', last_msg_id)
    #             print('Next ID Msg :', next_msg_id)
    #             if last_msg_id != next_msg_id:
    #                 print('Chut.......<3')
    #                 await channel.send('Chut.....:heart:')
    #                 last_msg_id = channel.last_message_id
    #             del channel
    #         await asyncio.sleep(60)

    async def background_task_twitch(self):
        await self.wait_until_ready()
        stream_date = dict()
        for i in user_logins:
            stream_date[i] = datetime.strptime('2020-01-01T00:00:00Z', '%Y-%m-%dT%H:%M:%SZ')
        while not self.is_closed():
            twitch = Twitch(api_twitch_id, api_twitch_secret)
            try:
                twitch.authenticate_app([])
            except:
                print('Erreur auth Twitch')
            streamers = twitch.get_streams(user_login=user_logins)
            channel = self.get_channel(int(chan_id_stream))
            twitch_stream = dict()
            for twitch_stream in streamers['data']:
                if (twitch_stream['type'] == 'live') and (stream_date[twitch_stream['user_name'].lower()]
                                                          < datetime.strptime(twitch_stream['started_at'],
                                                                              '%Y-%m-%dT%H:%M:%SZ')):
                    message = str()
                    message = 'Maintenant en stream :heart: !!!!!\n**'
                    message += twitch_stream['user_name']
                    message += '**\n'
                    message += 'Titre : ***'
                    message += twitch_stream['title']
                    message += '***\n'
                    message += 'sur **'
                    list_game = twitch.get_games(game_ids=twitch_stream['game_id'])
                    game_data = list_game['data'][0]
                    message += game_data['name']
                    message += '** pour **'
                    message += str(twitch_stream['viewer_count'])
                    message += '** viewers\n'
                    message += 'https://www.twitch.com/'
                    message += twitch_stream['user_name'].lower()
                    message += '\n'
                    print(message)
                    await channel.send(message)
                    stream_date[twitch_stream['user_name'].lower()] \
                        = datetime.strptime(twitch_stream['started_at'], '%Y-%m-%dT%H:%M:%SZ')
                    del message
            del streamers, twitch, twitch_stream
            del channel
            await asyncio.sleep(120)
