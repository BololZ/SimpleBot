import asyncio
from datetime import datetime
import uuid
import psycopg2
import psycopg2.extras

import discord
import yaml
from twitchAPI.twitch import Twitch
from twitchAPI.types import TwitchAPIException

with open("config.yml", 'r') as stream:
    try:
        cfg = yaml.safe_load(stream)
    except yaml.YAMLError as error:
        print(error)

chan_id_stream = cfg['twitch']['chan_id']
api_twitch_id = cfg['twitch']['client_id']
api_twitch_secret = cfg['twitch']['secret']
user_logins = cfg['twitch']['twitch_logins']
dsn_name = cfg['bdd']['name']
dsn_user = cfg['bdd']['user']
dsn_pwd = cfg['bdd']['pwd']
chan_id_birthday = cfg['birthday']['chan_id']
DSN = "dbname=" + dsn_name + " user=" + dsn_user + " password= " + dsn_pwd


class MonBot(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # create the background task and run it in the background
        self.bg_task_0 = self.loop.create_task(self.background_task_twitch())
        self.bg_task_1 = self.loop.create_task(self.background_task_birthday())

    async def on_ready(self):
        print('Logged on as', self.user)
        print('Chan_id_stream :', chan_id_stream)
        print('Chan_id_birthday :', chan_id_birthday)

    async def on_message(self, message):
        await self.wait_until_ready()
        # we do not want the bot to reply to itself
        if self.user.id == message.author.id or str(message.channel.type) != 'private':
            return None
        try:
            date_message = datetime.strptime(message.content, '%d/%m/%Y')
        except ValueError:
            await message.channel.send('Mauvais format de date ou aucune date')
            return 'Bad format'

        if date_message < datetime.date(datetime.today()):
            await message.channel.send('Mauvaise date dans le passé')
            return 'Bad date in the past'

        try:
            conn = psycopg2.connect(DSN)
            conn.set_client_encoding('UTF8')
        except psycopg2.Error as err:
            print('Erreur de connexion à la BDD: ', err)
            return err
        try:
            where = message.author.id
            curs = conn.cursor()
            curs.execute(
                'SELECT a.jour FROM identity as i, anniversaire as a WHERE i.id_simplebot = a.id_simplebot AND '
                'i.id_discord = %s;', [where])
            x = curs.fetchone()
            if x is None:
                uuid_id = uuid.uuid4()
                psycopg2.extras.register_uuid()
                curs.execute(
                    'INSERT INTO identity (id_simplebot, id_discord) VALUES (%(uuid)s,%(int)s);',
                    {'uuid': uuid_id, 'int': int(message.author.id)}
                )
                curs.execute(
                    'INSERT INTO anniversaire (id_simplebot, jour) VALUES (%(uuid)s,%(date)s);',
                    {'uuid': uuid_id, 'date': date_message}
                )
                await message.channel.send(
                    "Ta date d'anniversaire a été sauvegardée. Merci {0.author.name}.".format(message)
                )
            else:
                curs.execute(
                    'UPDATE anniversaire SET jour = %(date)s FROM identity WHERE '
                    'identity.id_simplebot = anniversaire.id_simplebot AND '
                    'identity.id_discord = %(int)s;', {'date': date_message, 'int': where}
                )
                await message.channel.send(
                    'Ta date d\'anniversaire a été mise à jour et sauvegardée. Merci {0.author.name}.'.format(message)
                )
        except psycopg2.Error as err:
            print('Erreur de requête : ', err)
            conn.rollback()
            conn.close()
            return err
        finally:
            conn.commit()
            conn.close()

    async def background_task_twitch(self):
        await self.wait_until_ready()
        stream_date = dict()
        for i in user_logins:
            stream_date[i] = datetime.strptime('2020-01-01T00:00:00Z', '%Y-%m-%dT%H:%M:%SZ')
        while not self.is_closed():
            twitch = Twitch(api_twitch_id, api_twitch_secret)
            print("Authentification Twitch...")
            try:
                twitch.authenticate_app([])
                print("Authentification Twitch réussie")
            except TwitchAPIException as exc:
                print('Erreur Authentification Twitch :', exc)
                del twitch
            finally:
                try:
                    streamers = twitch.get_streams(user_login=user_logins)
                except TwitchAPIException as exc:
                    print('Erreur get_streams Twitch :', exc)
                    del streamers
                finally:
                    channel = self.get_channel(int(chan_id_stream))
                    twitch_stream = dict()
                    for twitch_stream in streamers['data']:
                        if (twitch_stream['type'] == 'live') and (stream_date[twitch_stream['user_name'].lower()]
                                                                  < datetime.strptime(twitch_stream['started_at'],
                                                                                      '%Y-%m-%dT%H:%M:%SZ')):
                            print(twitch_stream['user_name'], " est en stream !")
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
                            await channel.send(message)
                            stream_date[twitch_stream['user_name'].lower()] \
                                = datetime.strptime(twitch_stream['started_at'], '%Y-%m-%dT%H:%M:%SZ')
                            del message
                    del streamers, twitch_stream
                    del channel
                    del twitch
            await asyncio.sleep(300)

    async def background_task_birthday(self):
        await self.wait_until_ready()
        while not self.is_closed():
            date_du_jour = datetime.date(datetime.today())
            try:
                conn = psycopg2.connect(DSN)
                conn.set_client_encoding("UTF8")
            except psycopg2.Error as err:
                print('Erreur de connexion :', err)
                return

            try:
                curs = conn.cursor()
                curs.execute(
                    'SELECT i.id_discord FROM identity as i, anniversaire as a WHERE i.id_simplebot = a.id_simplebot '
                    'AND a.jour = %s;', [date_du_jour]
                )
                x = curs.fetchall()
                for anniv in x:
                    if anniv is not None:
                        print("Anniv de ID : ", anniv[0])
                        user = self.get_user(anniv[0])
                        print("et pseudo : ", user)
                        channel = self.get_channel(chan_id_birthday)
                        await channel.send(
                            'Aujourd\'hui, ' + user.mention + ' est arrivé(e) dans ce monde ! '
                                                              ' Venez tous lui souhaiter un joyeux anniversaire ! '
                        )
                        date_prochaine = date_du_jour.replace(year=date_du_jour.year + 1)
                        curs.execute(
                            'UPDATE anniversaire SET jour = %(date)s FROM identity WHERE '
                            'identity.id_simplebot = anniversaire.id_simplebot AND '
                            'identity.id_discord = %(int)s;', {'date': date_prochaine, 'int': anniv[0]}
                        )
            except psycopg2.Error as err:
                print('Erreur de requête : ', err)
                conn.rollback()
                conn.close()
                return err
            finally:
                conn.commit()
                conn.close()
            await asyncio.sleep(900)
