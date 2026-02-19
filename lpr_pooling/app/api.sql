-- View: lpr.v_o2p
-- DROP VIEW lpr.v_o2p;
CREATE OR REPLACE VIEW lpr.v_o2p
 AS
 SELECT p.customer_id,
    v.camera_id AS entity_id,
    p.registration_number,
    p.car_owner,
    p.car_brand
   FROM lpr.v_origin_plate_3 v
     JOIN lpr.lpr_plate p ON v.customer_id = p.customer_id AND v.plate_id = p.id
  WHERE p.is_enabled AND CURRENT_TIMESTAMP >= p.valid_since AND CURRENT_TIMESTAMP <= p.valid_to;
ALTER TABLE lpr.v_o2p OWNER TO cnt;
GRANT ALL ON TABLE lpr.v_o2p TO cnt;
GRANT SELECT ON TABLE lpr.v_o2p TO lpr_demo;
GRANT SELECT ON TABLE lpr.v_o2p TO userfront;


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


-- FUNCTION: lpr.sync_all_by_plate_id(integer)
-- DROP FUNCTION IF EXISTS lpr.sync_all_by_plate_id(integer);
CREATE OR REPLACE FUNCTION lpr.sync_all_by_plate_id(plate_id_inp integer)
    RETURNS record
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
AS $BODY$
DECLARE
    r RECORD;
BEGIN
	SELECT camera_id, lpr.origin_sync(camera_id) as result
	INTO r
	FROM lpr.v_origin_plate_3 v
	LEFT JOIN lpr.lpr_origin o ON camera_id=entity_id
	LEFT JOIN billing.balance b using(customer_id)
	WHERE 1=1
	AND o.is_enabled
	AND NOT o.is_deleted
	AND NOW() <= b.end_date
	AND plate_id=plate_id_inp
	ORDER BY camera_id;

	RETURN r;
END;
$BODY$;
ALTER FUNCTION lpr.sync_all_by_plate_id(integer) OWNER TO cnt;


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


-- FUNCTION: lpr.api_camera_demo(integer, text, jsonb)
-- DROP FUNCTION IF EXISTS lpr.api_camera_demo(integer, text, jsonb);
CREATE OR REPLACE FUNCTION lpr.api_camera_demo(origin_id integer, entry text, data jsonb DEFAULT NULL::jsonb)
    RETURNS jsonb
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
AS $BODY$
DECLARE
	origin_id_inp INTEGER;
	image_plate TEXT;
	image_background TEXT;
	result_out JSONB;
	info_out JSONB;
	plates TEXT[];
BEGIN
IF entry = 'check_connection' THEN
	RETURN '{"result": true, "message": "Ok"}';
END IF;

origin_id_inp = origin_id;

IF entry = 'get_snapshot' THEN
	SELECT encode(image, 'base64') INTO image_background FROM lpr.lpr_demo_camera
	WHERE lpr.lpr_demo_camera.origin_id=origin_id_inp AND registration_number = 'snapshot'
	ORDER BY RANDOM() LIMIT 1;

	result_out = jsonb_build_object(
		'result', (image_background IS NOT NULL),
		'image', image_background
	);
	RETURN result_out;
END IF;

IF entry = 'get_event_images' THEN
	SELECT encode(image, 'base64') INTO image_plate FROM lpr.lpr_demo_camera
	WHERE lpr.lpr_demo_camera.origin_id=origin_id_inp AND registration_number = 'plate'
	ORDER BY RANDOM() LIMIT 1;
	
	SELECT encode(image, 'base64') INTO image_background FROM lpr.lpr_demo_camera
	JOIN lpr.lpr_event USING(registration_number)
	WHERE lpr.lpr_demo_camera.origin_id=origin_id_inp
	AND uuid = (data->>'uuid')::TEXT
	LIMIT 1;

	IF image_background IS NULL THEN
		SELECT encode(image, 'base64') INTO image_background FROM lpr.lpr_demo_camera
		WHERE lpr.lpr_demo_camera.origin_id=origin_id_inp AND registration_number IS NULL
		ORDER BY RANDOM() LIMIT 1;
	END IF;

	result_out = jsonb_build_object(
		'result', (image_plate IS NOT NULL) AND (image_background IS NOT NULL),
		'background', image_background,
		'object', image_plate
	);
	RETURN result_out;
END IF;

IF entry = 'make_action' THEN
	IF (data->>'action')::TEXT NOT IN ('check', 'get', 'info') THEN
		RETURN '{"result": false, "message": "Action not realized"}';
	END IF;

	IF (data->>'action')::TEXT = 'check' THEN
		RETURN '{"result": true, "message": "Ok"}';
	END IF;

	IF (data->>'action')::TEXT = 'get' THEN
		SELECT array_agg(registration_number) INTO plates
		FROM lpr.lpr_demo_camera
		WHERE lpr.lpr_demo_camera.origin_id=origin_id_inp AND registration_number IS NOT NULL
		AND registration_number NOT IN ('plate', 'snapshot');

		result_out = jsonb_build_object(
			'result', true,
			'plates', plates
		);
		RETURN result_out;
	END IF;

	IF (data->>'action')::TEXT = 'info' THEN
		SELECT jsonb_agg(
    	jsonb_build_object(
        	'id', registration_number,
        	'owner', car_owner,
        	'brand', car_brand
    	)
		) INTO info_out FROM lpr.lpr_demo_camera
		WHERE lpr.lpr_demo_camera.origin_id=origin_id_inp AND registration_number IS NOT NULL
		AND registration_number NOT IN ('plate', 'snapshot');

		result_out = jsonb_build_object(
			'result', (info_out IS NOT NULL),
			'info', info_out
		);
		RETURN result_out;
	END IF;
END IF;

RETURN '{"result": false, "message": "Something goes wrong"}';
END;
$BODY$;

ALTER FUNCTION lpr.api_camera_demo(integer, text, jsonb) OWNER TO cnt;
