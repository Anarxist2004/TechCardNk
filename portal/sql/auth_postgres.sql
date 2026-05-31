BEGIN;

CREATE TABLE IF NOT EXISTS public.users
(
    id bigserial NOT NULL,
    username text COLLATE pg_catalog."default" NOT NULL,
    password_hash text COLLATE pg_catalog."default" NOT NULL,
    salt text COLLATE pg_catalog."default" NOT NULL,
    full_name text COLLATE pg_catalog."default" NOT NULL DEFAULT '',
    "position" text COLLATE pg_catalog."default" NOT NULL DEFAULT '',
    company text COLLATE pg_catalog."default" NOT NULL DEFAULT '',
    created_at timestamp with time zone NOT NULL DEFAULT now(),
    updated_at timestamp with time zone NOT NULL DEFAULT now(),
    CONSTRAINT users_pkey PRIMARY KEY (id),
    CONSTRAINT users_username_key UNIQUE (username)
);

CREATE TABLE IF NOT EXISTS public.sessions
(
    token text COLLATE pg_catalog."default" NOT NULL,
    user_id bigint NOT NULL,
    expires_at timestamp with time zone NOT NULL,
    created_at timestamp with time zone NOT NULL DEFAULT now(),
    CONSTRAINT sessions_pkey PRIMARY KEY (token),
    CONSTRAINT sessions_user_id_fkey FOREIGN KEY (user_id)
        REFERENCES public.users (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE
);

ALTER TABLE IF EXISTS public.users
    ADD COLUMN IF NOT EXISTS full_name text COLLATE pg_catalog."default" NOT NULL DEFAULT '';

ALTER TABLE IF EXISTS public.users
    ADD COLUMN IF NOT EXISTS "position" text COLLATE pg_catalog."default" NOT NULL DEFAULT '';

ALTER TABLE IF EXISTS public.users
    ADD COLUMN IF NOT EXISTS company text COLLATE pg_catalog."default" NOT NULL DEFAULT '';

ALTER TABLE IF EXISTS public.users
    ADD COLUMN IF NOT EXISTS updated_at timestamp with time zone NOT NULL DEFAULT now();

CREATE INDEX IF NOT EXISTS sessions_user_id_idx
    ON public.sessions USING btree (user_id);

CREATE INDEX IF NOT EXISTS sessions_expires_at_idx
    ON public.sessions USING btree (expires_at);

COMMIT;
