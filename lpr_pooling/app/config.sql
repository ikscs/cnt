------------------------------------------------------------
-- LPR Global Config System
-- Schema: lpr
-- User:   cnt
------------------------------------------------------------

-- 1. Ensure schema exists
CREATE SCHEMA IF NOT EXISTS lpr AUTHORIZATION cnt;

------------------------------------------------------------
-- 2. Base config table (source of truth)
------------------------------------------------------------
CREATE TABLE IF NOT EXISTS lpr.config_source (
    key        text PRIMARY KEY,
    value      text NOT NULL,
    updated_at timestamptz NOT NULL DEFAULT now()
);

COMMENT ON TABLE  lpr.config_source IS 'Global application configuration (source table)';
COMMENT ON COLUMN lpr.config_source.key IS 'Configuration key';
COMMENT ON COLUMN lpr.config_source.value IS 'Configuration value';
COMMENT ON COLUMN lpr.config_source.updated_at IS 'Last update timestamp';


------------------------------------------------------------
-- 3. Materialized view for ultra-fast reads
------------------------------------------------------------
CREATE MATERIALIZED VIEW IF NOT EXISTS lpr.config AS
SELECT key, value FROM lpr.config_source;

COMMENT ON MATERIALIZED VIEW lpr.config IS
'Materialized cache of global config. Auto-refreshed by trigger.';


------------------------------------------------------------
-- 4. Refresh function (trigger target)
------------------------------------------------------------
CREATE OR REPLACE FUNCTION lpr.refresh_config()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    IF TG_OP = 'UPDATE' THEN
        NEW.updated_at := now();
        RETURN NEW;
    ELSIF TG_OP = 'INSERT' THEN
        NEW.updated_at := now();
        RETURN NEW;
    END IF;

    REFRESH MATERIALIZED VIEW lpr.config;
    RETURN NULL;
END;
$$;


------------------------------------------------------------
-- 5. Trigger to auto-refresh cache on every change
------------------------------------------------------------
DROP TRIGGER IF EXISTS trg_refresh_config ON lpr.config_source;

CREATE TRIGGER trg_refresh_config
AFTER INSERT OR UPDATE OR DELETE
ON lpr.config_source
FOR EACH STATEMENT
EXECUTE FUNCTION lpr.refresh_config();


------------------------------------------------------------
-- 6. Config accessor functions
------------------------------------------------------------

-- text
CREATE OR REPLACE FUNCTION lpr.cfg(k text)
RETURNS text
LANGUAGE plpgsql STABLE AS $$
DECLARE
    val text;
BEGIN
    SELECT value INTO val
    FROM lpr.config
    WHERE key = k;

    IF val IS NULL THEN
        RAISE EXCEPTION 'Unknown config key: %', k;
    END IF;

    RETURN val;
END;
$$;

-- integer
CREATE OR REPLACE FUNCTION lpr.cfg_int(k text)
RETURNS integer
LANGUAGE sql STABLE AS $$
    SELECT (value)::int FROM lpr.config WHERE key = $1;
$$;

-- boolean
CREATE OR REPLACE FUNCTION lpr.cfg_bool(k text)
RETURNS boolean
LANGUAGE sql STABLE AS $$
    SELECT (value)::bool FROM lpr.config WHERE key = $1;
$$;

-- jsonb
CREATE OR REPLACE FUNCTION lpr.cfg_json(k text)
RETURNS jsonb
LANGUAGE sql STABLE AS $$
    SELECT (value)::jsonb FROM lpr.config WHERE key = $1;
$$;


------------------------------------------------------------
-- 7. API view (for PostgREST)
------------------------------------------------------------
--CREATE OR REPLACE VIEW lpr.config_api AS
--SELECT key, value
--FROM lpr.config
--ORDER BY key;


------------------------------------------------------------
-- 8. Permissions for user "cnt"
------------------------------------------------------------

-- allow reading materialized view and API
GRANT SELECT ON lpr.config           TO lpr_user;
--GRANT SELECT ON lpr.config_api       TO cnt;
GRANT SELECT ON lpr.config_source    TO lpr_user;

-- allow modifying config (optional)
GRANT INSERT, UPDATE, DELETE ON lpr.config_source TO cnt;

-- allow execution of config functions
GRANT EXECUTE ON FUNCTION lpr.cfg(text)      TO lpr_user;
GRANT EXECUTE ON FUNCTION lpr.cfg_int(text)  TO lpr_user;
GRANT EXECUTE ON FUNCTION lpr.cfg_bool(text) TO lpr_user;
GRANT EXECUTE ON FUNCTION lpr.cfg_json(text) TO lpr_user;

------------------------------------------------------------
-- DONE
------------------------------------------------------------
