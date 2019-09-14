import asyncio
import datetime
import discord

global chan_id

class MyClient(discord.AutoShardedClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # create the background task and run it in the background
        self.bg_task = self.loop.create_task(self.backgroung_task_chut())

    async def on_ready(self):
        print('Logged on as', self.user)
        print(chan_id)

    async def backgroung_task_chut(self):
        await self.wait_until_ready()
        channel = self.get_channel(int(chan_id))  # channel ID goes here Bolol
        while not self.is_closed():
            heure = datetime.datetime.now()
            h = str(heure.hour)
            m = str(heure.minute)
            print(h+':'+m)
            if int(h) == 22 and int(m) == 0:
                print('Chut.......<3')
                await channel.send('Chut.....:heart:', tts=True)
            await asyncio.sleep(60)
