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
        print('Chan_id :', chan_id)

    async def backgroung_task_chut(self):
        await self.wait_until_ready()
        channel = self.get_channel(int(chan_id))
        last_msg_id = channel.last_message_id
        while not self.is_closed():
            heure = datetime.datetime.now()
            h = str(heure.hour)
            m = str(heure.minute)
            print(h+':'+m)
            next_msg_id = channel.last_message_id
            print('Last ID Msg :', last_msg_id)
            print('Next ID Msg :',next_msg_id)
            if (int(h) >= 22 or int(h) <=5) and (int(m)%30 == 0):
                if last_msg_id != next_msg_id:
                    print('Chut.......<3')
                    await channel.send('Chut.....:heart:')
                    last_msg_id = channel.last_message_id
            await asyncio.sleep(60)
