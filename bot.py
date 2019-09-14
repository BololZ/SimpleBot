import discord
import datetime


class MyClient(discord.AutoShardedClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # create the background task and run it in the background
        self.bg_task = self.loop.create_task(self.my_background_task())

    async def on_ready(self):
        print('Logged on as', self.user)

    async def my_background_task(self):
        await self.wait_until_ready()
        channel = self.get_channel(338723133462806528)  # channel ID goes here
        heure = datetime.time(datetime.now())
        h = str(heure.hour)
        m = str(heure.minute)
        if int(h) == 22 and int(m) == 0:
            print('Chut.......<3')
            await channel.send('Chut.....<3')
            await asyncio.sleep(60)
