import logging
import bot
import yaml
import discord

logger0 = logging.getLogger('discord')
logger0.setLevel(logging.INFO)
handler0 = logging.FileHandler(filename='log/discord.log', encoding='utf-8', mode='w')
handler0.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger0.addHandler(handler0)

logger1 = logging.getLogger('twitchAPI')
logger1.setLevel(logging.INFO)
handler1 = logging.FileHandler(filename='log/twitch.log', encoding='utf-8', mode='w')
handler1.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger1.addHandler(handler1)

with open("config.yml", 'r') as stream:
    try:
        cfg = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)
token = cfg['client']['token']

intents = discord.Intents.default()
intents.members = True
MemberCacheFlags = discord.MemberCacheFlags.all()

bot_discord = bot.MonBot(intents=intents, MemberCacheFlags=MemberCacheFlags)
try:
    bot_discord.run(token)
except bot_discord.ClientException as Err:
    print('Erreur de lancement : ', Err)
