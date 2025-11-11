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
