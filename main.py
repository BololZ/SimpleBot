# import logging
from sys import exit
import bot
import yaml
import discord

# logger0 = logging.getLogger('discord')
# logger0.setLevel(logging.INFO)
# handler0 = logging.FileHandler(filename='log/discord.log', encoding='utf-8', mode='w')
# handler0.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
# logger0.addHandler(handler0)

try:
    with open("config.yaml", 'r') as stream:
        try:
            cfg = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print("Erreur avec le fichier de configuration : ", exc)
            exit(1)
        else:
            token = cfg['client']['token']
            stream.close()
            intents = discord.Intents.default()
            intents.members = True
            MemberCacheFlags = discord.MemberCacheFlags.all()
            bot_discord = bot.MonBot(
                reconnect=True, intents=intents, MemberCacheFlags=MemberCacheFlags)
            try:
                bot_discord.run(token)
            except discord.ClientException as Err:
                print('Erreur de lancement du bot : ', Err)
                exit(1)
except IOError as exec:
    print("Erreur d'accès au fichier config.yaml : ", exec)
    exit(1)
