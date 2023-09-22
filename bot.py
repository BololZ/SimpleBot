import asyncio
from datetime import datetime, timezone
import uuid
import psycopg

import discord
import yaml
from twitchAPI.twitch import Twitch
from twitchAPI.types import TwitchAPIException

try:
    with open("config.yaml", 'r') as stream:
        try:
            cfg = yaml.safe_load(stream)
        except yaml.YAMLError as error:
            print(error)
            exit(1)
        else:
            chan_id_stream = cfg['twitch']['chan_id']
            api_twitch_id = cfg['twitch']['client_id']
            api_twitch_secret = cfg['twitch']['secret']
            twitch_logins = cfg['twitch']['twitch_logins']
            dsn_name = cfg['bdd']['name']
            dsn_host = cfg['bdd']['host']
            dsn_user = cfg['bdd']['user']
            dsn_pwd = cfg['bdd']['pwd']
            chan_id_birthday = cfg['birthday']['chan_id']
            DSN = "dbname=" + dsn_name + " user=" + dsn_user + \
                " password= " + dsn_pwd + " host=" + dsn_host
            stream.close()
except IOError as exec:
    print("Erreur d'accès à la configuration : ", exec)
    exit(1)


class MonBot(discord.Client):
    async def setup_hook(self):
        self.loop.create_task(self.background_task_twitch())
        self.loop.create_task(self.background_task_birthday())

    async def on_ready(self: discord.Client):
        print('Logged on as', self.user)
        print('Chan_id_stream :', chan_id_stream)
        print('Chan_id_birthday :', chan_id_birthday)

    async def on_message(self: discord.Client, message: discord.Message):
        await self.wait_until_ready()
        # we do not want the bot to reply to itself and public message
        assert self.user is not None, "Discord.User None"
        if self.user.id == message.author.id or str(message.channel.type) != 'private':
            return None
        try:
            date_message = datetime.strptime(message.content, '%d/%m/%Y')
        except ValueError:
            await message.channel.send('Mauvais format de date ou aucune date')
            return 'Bad format'

        if date_message < datetime.today():
            await message.channel.send('Mauvaise date dans le passé')
            return 'Bad date in the past'

        try:
            conn = psycopg.connect(DSN)
            # conn.set_client_encoding('UTF8')
        except psycopg.Error as err:
            print('Erreur de connexion à la BDD: ', err)
        else:
            try:
                where = message.author.id
                curs = conn.cursor()
                curs.execute(
                    'SELECT a.jour FROM identity as i, anniversaire as a WHERE i.id_simplebot = a.id_simplebot AND '
                    'i.id_discord = %s;', [where])
                x = curs.fetchone()
            except psycopg.Error as err:
                print('Erreur de SELECT : ', err)
                conn.close()
            else:
                if x is None:
                    uuid_id = uuid.uuid4()
                    # psycopg.extras.register_uuid()
                    try:
                        curs.execute(
                            'INSERT INTO identity (id_simplebot, id_discord) VALUES (%(uuid)s,%(int)s);',
                            {'uuid': uuid_id, 'int': int(message.author.id)}
                        )
                        curs.execute(
                            'INSERT INTO anniversaire (id_simplebot, jour) VALUES (%(uuid)s,%(date)s);',
                            {'uuid': uuid_id, 'date': date_message}
                        )
                    except psycopg.Error as err:
                        print("Erreur d'INSERT : ", err)
                        conn.rollback()
                        conn.close()
                    else:
                        await message.channel.send(
                            "Ta date d'anniversaire a été sauvegardée. Merci {0.author.name}.".format(
                                message)
                        )
                        conn.commit()
                        conn.close()
                else:
                    try:
                        curs.execute(
                            'UPDATE anniversaire SET jour = %(date)s FROM identity WHERE '
                            'identity.id_simplebot = anniversaire.id_simplebot AND '
                            'identity.id_discord = %(int)s;', {
                                'date': date_message, 'int': where}
                        )
                    except psycopg.Error as err:
                        print("Erreur d'UPDATE : ", err)
                        conn.rollback()
                        conn.close()
                    else:
                        await message.channel.send(
                            'Ta date d\'anniversaire a été mise à jour et sauvegardée. Merci {0.author.name}.'.format(
                                message)
                        )
                        conn.commit()
                        conn.close()

    async def background_task_twitch(self: discord.Client):
        await self.wait_until_ready()
        stream_date = dict()
        for i in twitch_logins:
            stream_date[i] = datetime(2023, 1, 1, tzinfo=timezone.utc)
        while not self.is_closed():
            twitch = await Twitch(api_twitch_id, api_twitch_secret)
            # print("Authentification Twitch...")
            try:
                # print("Authentification Twitch réussie")
                try:
                    streamers = dict()
                    channel = self.get_channel(int(chan_id_stream))
                    streamers = twitch.get_streams(user_login=twitch_logins)
                    async for twitch_stream in streamers:
                        if (stream_date[twitch_stream.user_name.lower()] < twitch_stream.started_at):
                            print(twitch_stream.user_name,
                                  " est en stream !")
                            msg = 'Maintenant en stream :heart: !!!!!\n**'
                            msg += twitch_stream.user_name
                            msg += '**\n'
                            msg += 'Titre : ***'
                            msg += twitch_stream.title
                            msg += '***\n'
                            msg += 'sur **'
                            msg += twitch_stream.game_name
                            msg += '** pour **'
                            msg += str(twitch_stream.viewer_count)
                            msg += '** viewers\n'
                            msg += 'https://www.twitch.com/'
                            msg += twitch_stream.user_name.lower()
                            msg += '\n'
                            try:
                                await channel.send(msg)  # type: ignore
                            except discord.ClientException as err:
                                print("Erreur envoi message : ", err)
                            stream_date[twitch_stream.user_name.lower(
                            )] = twitch_stream.started_at
                            del msg, twitch_stream
                    del channel, streamers
                except TwitchAPIException as exc:
                    print('Erreur Twitch API get_streams : ', exc)
            except TwitchAPIException as exc:
                print('Erreur API Auth Twitch : ', exc)
            finally:
                del twitch
            await asyncio.sleep(300)

    async def background_task_birthday(self: discord.Client):
        await self.wait_until_ready()
        while not self.is_closed():
            date_du_jour = datetime.date(datetime.today())
            try:
                conn = psycopg.connect(DSN)
            except psycopg.Error as err:
                print('Erreur de connexion : ', err)
            else:
                # conn.set_client_encoding("UTF8")
                try:
                    curs = conn.cursor()
                    curs.execute(
                        'SELECT i.id_discord FROM identity as i, anniversaire as a WHERE i.id_simplebot = a.id_simplebot '
                        'AND a.jour = %s;', [date_du_jour]
                    )
                    x = curs.fetchall()
                except psycopg.Error as err:
                    print('Erreur de SELECT : ', err)
                    conn.close()
                else:
                    for anniv in x:
                        if anniv is not None:
                            print("Anniv de ID : ", anniv[0])
                            user = self.get_user(anniv[0])
                            print("et pseudo : ", user)
                            channel = self.get_channel(chan_id_birthday)
                            if user != None:
                                msg = 'Aujourd\'hui, ' + user.mention + \
                                    ' est arrivé(e) dans ce monde !\n Venez tous/tes lui souhaiter un joyeux anniversaire ! '
                                try:
                                    await channel.send(msg)  # type: ignore
                                except discord.ClientException as err:
                                    print("Erreur envoi message : ", err)
                                else:
                                    date_prochaine = date_du_jour.replace(
                                        year=date_du_jour.year + 1)
                                    try:
                                        curs.execute(
                                            'UPDATE anniversaire SET jour = %(date)s FROM identity WHERE '
                                            'identity.id_simplebot = anniversaire.id_simplebot AND '
                                            'identity.id_discord = %(int)s;', {
                                                'date': date_prochaine, 'int': anniv[0]})
                                    except psycopg.Error as err:
                                        print("Erreur d'update: ", err)
                                        conn.close()
                                    else:
                                        conn.commit()
                    conn.close()
            await asyncio.sleep(900)
