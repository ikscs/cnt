CREATE TABLE IF NOT EXISTS public.wireguard_conf (
    "id" SERIAL NOT NULL,
    "name" TEXT NULL DEFAULT NULL,
    "customer_id" NUMERIC NOT NULL,
    "conf" TEXT NOT NULL,
    "enabled" BOOLEAN NOT NULL DEFAULT true,
    "comment" TEXT NULL DEFAULT NULL,
    PRIMARY KEY ("id"),
    CONSTRAINT "FK_wireguard_conf_customer" FOREIGN KEY ("customer_id") REFERENCES "customer" ("customer_id") ON UPDATE NO ACTION ON DELETE NO ACTION
)
COMMENT='WireGuard configuration collection';
ALTER TABLE IF EXISTS public.wireguard_conf OWNER to cnt;

CREATE TABLE IF NOT EXISTS public.wireguard_port (
    "listen_port" SERIAL NOT NULL,
    "conf_id" INTEGER NOT NULL,
    "host" TEXT NOT NULL,
    "port" INTEGER NOT NULL,
    "enabled" BOOLEAN NOT NULL DEFAULT true,
    "comment" TEXT NULL DEFAULT NULL,
    PRIMARY KEY ("listen_port"),
    UNIQUE ("conf_id", "host", "port"),
    CONSTRAINT "FK_wireguard_port_wireguard_conf" FOREIGN KEY ("conf_id") REFERENCES "wireguard_conf" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION
)
COMMENT='WireGuard ports collection';
ALTER TABLE IF EXISTS public.wireguard_port OWNER to cnt;

CREATE OR REPLACE FUNCTION public.wg_update_event()
    RETURNS trigger
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE NOT LEAKPROOF
AS $BODY$
DECLARE
    base TEXT;
    url TEXT;
BEGIN
    SELECT lpr.cfg('wg_agg_base') INTO base;
    IF base IS NULL THEN RETURN NULL; END IF;
    url = base || '/reload';
    PERFORM http_get(url);
    RETURN NULL;
END;
$BODY$;
ALTER FUNCTION public.wg_update_event() OWNER TO cnt;

CREATE OR REPLACE TRIGGER on_change_wg_conf
    AFTER INSERT OR DELETE OR TRUNCATE OR UPDATE 
    ON public.wireguard_conf
    FOR EACH STATEMENT
    EXECUTE FUNCTION public.wg_update_event();

CREATE OR REPLACE TRIGGER on_change_wg_port
    AFTER INSERT OR DELETE OR TRUNCATE OR UPDATE 
    ON public.wireguard_port
    FOR EACH STATEMENT
    EXECUTE FUNCTION public.wg_update_event();
