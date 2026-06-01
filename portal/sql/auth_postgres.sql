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

ALTER TABLE IF EXISTS public.tech_cards
    ADD COLUMN IF NOT EXISTS user_id bigint;

DO $$
BEGIN
    IF to_regclass('public.tech_cards') IS NOT NULL AND NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'tech_cards_user_id_fkey'
    ) THEN
        ALTER TABLE public.tech_cards
            ADD CONSTRAINT tech_cards_user_id_fkey FOREIGN KEY (user_id)
            REFERENCES public.users (id) MATCH SIMPLE
            ON UPDATE NO ACTION
            ON DELETE SET NULL;
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS tech_cards_user_id_idx
    ON public.tech_cards USING btree (user_id);

CREATE TABLE IF NOT EXISTS public.tech_card_images
(
    id bigserial NOT NULL,
    tech_card_id bigint NOT NULL,
    image_url text COLLATE pg_catalog."default" NOT NULL,
    created_at timestamp with time zone NOT NULL DEFAULT now(),
    CONSTRAINT tech_card_images_pkey PRIMARY KEY (id),
    CONSTRAINT tech_card_images_tech_card_id_fkey FOREIGN KEY (tech_card_id)
        REFERENCES public.tech_cards (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS tech_card_images_tech_card_id_idx
    ON public.tech_card_images USING btree (tech_card_id);

CREATE UNIQUE INDEX IF NOT EXISTS tech_card_images_card_url_idx
    ON public.tech_card_images USING btree (tech_card_id, image_url);

CREATE TABLE IF NOT EXISTS public.tech_card_image_descriptions
(
    id bigserial NOT NULL,
    image_id bigint NOT NULL,
    user_id bigint,
    description text COLLATE pg_catalog."default" NOT NULL,
    is_ai_generated boolean NOT NULL DEFAULT false,
    created_at timestamp with time zone NOT NULL DEFAULT now(),
    CONSTRAINT tech_card_image_descriptions_pkey PRIMARY KEY (id),
    CONSTRAINT tech_card_image_descriptions_image_id_fkey FOREIGN KEY (image_id)
        REFERENCES public.tech_card_images (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE,
    CONSTRAINT tech_card_image_descriptions_user_id_fkey FOREIGN KEY (user_id)
        REFERENCES public.users (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS tech_card_image_descriptions_image_id_idx
    ON public.tech_card_image_descriptions USING btree (image_id);

CREATE INDEX IF NOT EXISTS tech_card_image_descriptions_user_id_idx
    ON public.tech_card_image_descriptions USING btree (user_id);

CREATE TABLE IF NOT EXISTS public.expert_image_annotations
(
    id bigserial NOT NULL,
    image_key text COLLATE pg_catalog."default" NOT NULL,
    image_url text COLLATE pg_catalog."default",
    image_name text COLLATE pg_catalog."default",
    user_id bigint,
    file_path text COLLATE pg_catalog."default" NOT NULL,
    created_at timestamp with time zone NOT NULL DEFAULT now(),
    CONSTRAINT expert_image_annotations_pkey PRIMARY KEY (id),
    CONSTRAINT expert_image_annotations_user_id_fkey FOREIGN KEY (user_id)
        REFERENCES public.users (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS expert_image_annotations_image_key_idx
    ON public.expert_image_annotations USING btree (image_key);

CREATE INDEX IF NOT EXISTS expert_image_annotations_user_id_idx
    ON public.expert_image_annotations USING btree (user_id);

CREATE TABLE IF NOT EXISTS public.expert_image_protocols
(
    id bigserial NOT NULL,
    image_key text COLLATE pg_catalog."default" NOT NULL,
    image_url text COLLATE pg_catalog."default",
    image_name text COLLATE pg_catalog."default",
    user_id bigint,
    file_path text COLLATE pg_catalog."default" NOT NULL,
    protocol_data jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamp with time zone NOT NULL DEFAULT now(),
    CONSTRAINT expert_image_protocols_pkey PRIMARY KEY (id),
    CONSTRAINT expert_image_protocols_user_id_fkey FOREIGN KEY (user_id)
        REFERENCES public.users (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS expert_image_protocols_image_key_idx
    ON public.expert_image_protocols USING btree (image_key);

CREATE INDEX IF NOT EXISTS expert_image_protocols_user_id_idx
    ON public.expert_image_protocols USING btree (user_id);

COMMIT;
