import logging
import bot

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='log/discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


client = bot.MyClient()
client.run('NjIwNDc0OTkyNjA5NzIyMzg3.XXXbhA.bcr9VOVoj11NujMumGcsK0lleW8')
