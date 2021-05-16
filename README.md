# SimpleBot
##config.yml
    client:
        token: 
        chan_id: 
    twitch:
        client_id: 
        secret: 
        twitch_logins: ['lesgueteuses', 'bololtv', 'siraza', 'papydje', 'ovniiii', 'nutcrewtv', 'cltron_', 'maeryth']
        chan_id: 
    bdd:
        name: 'simplebot'
        user: 'simplebot'
        pwd: 
    birthday:
        chan_id: 

##PostgreSQL Schema

    CREATE DATABASE simplebot
        WITH 
        OWNER = simplebot
        ENCODING = 'UTF8'
        LC_COLLATE = 'fr_FR.UTF-8'
        LC_CTYPE = 'fr_FR.UTF-8'
        TABLESPACE = pg_default
        CONNECTION LIMIT = -1;