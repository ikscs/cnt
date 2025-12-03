-- FUNCTION: lpr.get_last_dt(integer)
-- DROP FUNCTION IF EXISTS lpr.get_last_dt(integer);
CREATE OR REPLACE FUNCTION lpr.get_last_dt(entity_id_inp integer)
    RETURNS timestamp with time zone
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
AS $BODY$
DECLARE
result_ts TIMESTAMPTZ;
BEGIN
    SELECT INTO result_ts ts_start FROM lpr.lpr_event WHERE entity_id=entity_id_inp ORDER BY id DESC LIMIT 1;
	IF result_ts IS NOT NULL THEN RETURN result_ts; END IF;

    --Alternative ts
	--SELECT INTO result_ts ts FROM pcnt.event_crossline WHERE origin=origin_inp ORDER BY ts DESC LIMIT 1;
	--IF result_ts IS NOT NULL THEN RETURN result_ts; END IF;

	RETURN CURRENT_DATE::TIMESTAMPTZ;
END
$BODY$;
ALTER FUNCTION lpr.get_last_dt(integer) OWNER TO cnt;


-- FUNCTION: lpr.get_snapshot(integer)
-- DROP FUNCTION IF EXISTS lpr.get_snapshot(integer);
CREATE OR REPLACE FUNCTION lpr.get_snapshot(origin_id integer)
    RETURNS jsonb
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
AS $BODY$
DECLARE
    result JSONB;
BEGIN
    SELECT lpr.api_camera(origin_id, 'get_snapshot') INTO result;
    RETURN result;
END;
$BODY$;
ALTER FUNCTION lpr.get_snapshot(integer) OWNER TO cnt;


-- FUNCTION: lpr.get_event_images(integer, text)
-- DROP FUNCTION IF EXISTS lpr.get_event_images(integer, text);
CREATE OR REPLACE FUNCTION lpr.get_event_images(origin_id integer, uuid text)
    RETURNS jsonb
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
AS $BODY$
DECLARE
    result JSONB;
BEGIN
    SELECT lpr.api_camera(origin_id, 'get_event_images', jsonb_build_object('uuid', uuid)) INTO result;
    RETURN result;
END;
$BODY$;
ALTER FUNCTION lpr.get_event_images(integer, text) OWNER TO cnt;


-- FUNCTION: lpr.origin_sync(integer)
-- DROP FUNCTION IF EXISTS lpr.origin_sync(integer);
CREATE OR REPLACE FUNCTION lpr.origin_sync(origin_id integer)
    RETURNS jsonb
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
AS $BODY$
DECLARE
    plates TEXT[];
BEGIN
	SELECT array_agg(registration_number) INTO plates FROM lpr.lpr_o2p
	JOIN lpr.lpr_origin o USING(entity_id)
	JOIN lpr.lpr_origin_type t USING(origin_type_id)
	WHERE protocol='ISAPI' AND vendor IN ('Tyto')
	AND is_enabled AND NOT is_deleted AND entity_id=origin_id;

	--RAISE INFO 'plates=%', plates;
	IF plates IS NULL THEN
		RETURN NULL;
	END IF;

	--RETURN lpr.plates_action(origin_id, 'sync', plates);
	RETURN lpr.api_camera(origin_id, 'make_action', jsonb_build_object('action', 'sync', 'plates', plates));

END;
$BODY$;
ALTER FUNCTION lpr.origin_sync(integer) OWNER TO cnt;


-- FUNCTION: lpr.origin_sync_full(integer)
-- DROP FUNCTION IF EXISTS lpr.origin_sync_full(integer);
CREATE OR REPLACE FUNCTION lpr.origin_sync_full(origin_id integer)
    RETURNS jsonb
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
AS $BODY$
DECLARE
    plates TEXT[];
    brands TEXT[];
    owners TEXT[];
BEGIN
	SELECT array_agg(registration_number ORDER BY registration_number),
	array_agg(car_owner ORDER BY registration_number),
	array_agg(car_brand ORDER BY registration_number)
	INTO plates, owners, brands FROM lpr.v_o2p
	JOIN lpr.lpr_origin o USING(entity_id)
	JOIN lpr.lpr_origin_type t USING(origin_type_id)
	WHERE protocol='ISAPI' AND vendor IN ('Tyto')
	AND is_enabled AND NOT is_deleted AND entity_id=origin_id;

	--RAISE INFO 'plates=%', plates;
	--RAISE INFO 'brands=%', brands;
	--RAISE INFO 'owners=%', owners;
	IF plates IS NULL THEN
		RETURN NULL;
	END IF;

	RETURN lpr.plates_modify(origin_id, plates, brands, owners);
END;
$BODY$;
ALTER FUNCTION lpr.origin_sync_full(integer) OWNER TO cnt;


-- PROCEDURE: lpr.lpr_upload_events(integer, jsonb)
-- DROP PROCEDURE IF EXISTS lpr.lpr_upload_events(integer, jsonb);
CREATE OR REPLACE PROCEDURE lpr.lpr_upload_events(IN origin_id integer, IN plate_events jsonb)
LANGUAGE 'plpgsql'
AS $BODY$
BEGIN
    --RAISE NOTICE 'in %', plate_events;

    CREATE TEMP TABLE tmp_table_otp1
    ON COMMIT DROP
    AS
    SELECT *
    FROM jsonb_to_recordset(plate_events) AS x(
        ts_start TIMESTAMPTZ,
	matched_number TEXT
    );

    UPDATE lpr.lpr_plate SET valid_to=CURRENT_TIMESTAMP
    WHERE id IN (
	SELECT p.id FROM tmp_table_otp1 t
	JOIN lpr.v_origin_plate o ON o.camera_id=origin_id
	JOIN lpr.lpr_plate p ON p.customer_id=o.customer_id AND p.registration_number=t.matched_number
	WHERE 1=1
	AND p.is_otp
	AND t.ts_start BETWEEN p.valid_since and p.valid_to
    );
END;
$BODY$;
ALTER PROCEDURE lpr.lpr_upload_events(integer, jsonb) OWNER TO cnt;
