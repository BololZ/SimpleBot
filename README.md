# SimpleBot

   config.yaml
    
        client:
            token: 
            chan_id: 
        twitch:
            client_id: 
            secret: 
            twitch_logins: [,]
            chan_id: 
        bdd:
            name: 'simplebot'
            user: 'simplebot'
            pwd: 
        birthday:
            chan_id: 

   PostgreSQL Schema

        CREATE DATABASE simplebot
            WITH 
            OWNER = simplebot
            ENCODING = 'UTF8'
            LC_COLLATE = 'fr_FR.UTF-8'
            LC_CTYPE = 'fr_FR.UTF-8'
            TABLESPACE = pg_default
            CONNECTION LIMIT = -1;
    
        CREATE TABLE public.anniversaire (
            id_simplebot uuid NOT NULL,
            jour date NOT NULL
            );

        ALTER TABLE public.anniversaire OWNER TO simplebot;

        CREATE TABLE public.identity (
            id_simplebot uuid NOT NULL,
            id_discord bigint NOT NULL
        );


        ALTER TABLE public.identity OWNER TO simplebot;

        ALTER TABLE ONLY public.anniversaire
            ADD CONSTRAINT anniversaire_pkey PRIMARY KEY (id_simplebot);

        ALTER TABLE ONLY public.identity
            ADD CONSTRAINT identity_pkey PRIMARY KEY (id_simplebot);

        ALTER TABLE ONLY public.anniversaire
            ADD CONSTRAINT anniversaire_id_simplebot_fkey FOREIGN KEY (id_simplebot) REFERENCES public.identity(id_simplebot) ON DELETE CASCADE;
