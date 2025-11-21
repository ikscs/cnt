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
    RETURNS lpr."image/jpeg"
    LANGUAGE 'plpython3u'
    COST 100
    VOLATILE PARALLEL UNSAFE
AS $BODY$
import sys
import json
import base64

script_dir = '/opt/docker/lpr_pooling/app'

if script_dir not in sys.path:
    sys.path.append(script_dir)

from camera_tyto import Camera

sql = f"""SELECT credentials::JSONB FROM lpr.lpr_origin JOIN lpr.lpr_origin_type USING(origin_type_id)
WHERE protocol='ISAPI' AND vendor IN ('Tyto')
AND is_enabled AND NOT is_deleted AND entity_id={origin_id}"""

query = plpy.execute(sql)
if not query:
    return None
credentials = json.loads(query[0]['credentials'])

camera = Camera(credentials)
if not camera.is_connected:
    return None

blob = camera.get_snapshot()
if not blob:
    return None

plpy.execute("""
    SELECT set_config(
        'response.headers',
        '[{"Content-Type": "image/jpeg"}, {"Content-Disposition": "inline; filename=\\"snapshot.jpg\\""}]',
        true
    );
""")

return base64.b64decode(blob)
$BODY$;
ALTER FUNCTION lpr.get_snapshot(integer) OWNER TO cnt;


-- FUNCTION: lpr.plates_action(integer, text, text[])
-- DROP FUNCTION IF EXISTS lpr.plates_action(integer, text, text[]);
CREATE OR REPLACE FUNCTION lpr.plates_action(origin_id integer,	action text, plates text[] DEFAULT NULL::text[])
    RETURNS jsonb
    LANGUAGE 'plpython3u'
    COST 100
    VOLATILE PARALLEL UNSAFE
AS $BODY$
import sys
import json

script_dir = '/opt/docker/lpr_pooling/app'

if script_dir not in sys.path:
    sys.path.append(script_dir)

from camera_tyto import Camera

sql = f"""SELECT credentials::JSONB FROM lpr.lpr_origin JOIN lpr.lpr_origin_type USING(origin_type_id)
WHERE protocol='ISAPI' AND vendor IN ('Tyto')
AND is_enabled AND NOT is_deleted AND entity_id={origin_id}"""

query = plpy.execute(sql)
if not query:
    return None
credentials = json.loads(query[0]['credentials'])

camera = Camera(credentials)
if not camera.is_connected:
    return None

result = camera.make_action(action, plates)
if not result:
    return None

return json.dumps(result, ensure_ascii=False)
$BODY$;
ALTER FUNCTION lpr.plates_action(integer, text, text[]) OWNER TO cnt;


-- FUNCTION: lpr.plates_modify(integer, text[], text[], text[])
-- DROP FUNCTION IF EXISTS lpr.plates_modify(integer, text[], text[], text[]);
CREATE OR REPLACE FUNCTION lpr.plates_modify(origin_id integer, plates text[], brands text[], owners text[])
    RETURNS jsonb
    LANGUAGE 'plpython3u'
    COST 100
    VOLATILE PARALLEL UNSAFE
AS $BODY$
import sys
import json

script_dir = '/opt/docker/lpr_pooling/app'

if script_dir not in sys.path:
    sys.path.append(script_dir)

from camera_tyto import Camera

sql = f"""SELECT credentials::JSONB FROM lpr.lpr_origin JOIN lpr.lpr_origin_type USING(origin_type_id)
WHERE protocol='ISAPI' AND vendor IN ('Tyto')
AND is_enabled AND NOT is_deleted AND entity_id={origin_id}"""

query = plpy.execute(sql)
if not query:
    return None
credentials = json.loads(query[0]['credentials'])

camera = Camera(credentials)
if not camera.is_connected:
    return None

result = camera.make_action('modify', plates, brands, owners)
if not result:
    return None

return json.dumps(result, ensure_ascii=False)
$BODY$;
ALTER FUNCTION lpr.plates_modify(integer, text[], text[], text[]) OWNER TO cnt;


-- FUNCTION: lpr.get_event_images(integer, text)
-- DROP FUNCTION IF EXISTS lpr.get_event_images(integer, text);
CREATE OR REPLACE FUNCTION lpr.get_event_images(origin_id integer, uuid text)
    RETURNS jsonb
    LANGUAGE 'plpython3u'
    COST 100
    VOLATILE PARALLEL UNSAFE
AS $BODY$
import sys
import json

script_dir = '/opt/docker/lpr_pooling/app'

if script_dir not in sys.path:
    sys.path.append(script_dir)

from camera_tyto import Camera

sql = f"""SELECT credentials::JSONB FROM lpr.lpr_origin JOIN lpr.lpr_origin_type USING(origin_type_id)
WHERE protocol='ISAPI' AND vendor IN ('Tyto')
AND is_enabled AND NOT is_deleted AND entity_id={origin_id}"""

query = plpy.execute(sql)
if not query:
    return None
credentials = json.loads(query[0]['credentials'])
	
camera = Camera(credentials)
if not camera.is_connected:
    return None

result = camera.get_by_uuid(uuid)

if not result:
    return None

return json.dumps(result, ensure_ascii=False)
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

	RETURN lpr.plates_action(origin_id, 'sync', plates);
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
