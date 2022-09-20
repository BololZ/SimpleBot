# import logging
import bot
import yaml
import discord

# logger0 = logging.getLogger('discord')
# logger0.setLevel(logging.INFO)
# handler0 = logging.FileHandler(filename='log/discord.log', encoding='utf-8', mode='w')
# handler0.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
# logger0.addHandler(handler0)

with open("config.yaml", 'r') as stream:
    try:
        cfg = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)
    finally:
        token = cfg['client']['token']

intents = discord.Intents.default()
intents.members = True
MemberCacheFlags = discord.MemberCacheFlags.all()

bot_discord = bot.MonBot(intents=intents, MemberCacheFlags=MemberCacheFlags)
try:
    bot_discord.run(token)
except discord.ClientException as Err:
    print('Erreur de lancement : ', Err)
