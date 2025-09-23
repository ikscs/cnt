from telegram_bot import TBot

ALARM_STATUS = ['Error', 'Unhealthy']

def load_alarms(data):
    res = dict()
    for id, val in data.items():
        res[id] = set()
        status = val.get('status', {})
        for k, v in status.items():
            if v in ALARM_STATUS:
                res[id].add(k)
    return {k: v for k, v in res.items() if v}

def get_fresh_alarms(old_alarms, new_alarms):
    fresh_alarms = dict()
    for k, v in new_alarms.items():
        if k not in old_alarms:
            fresh_alarms[k] = v
        else:
            delta = v - old_alarms[k]
            if delta:
                fresh_alarms[k] = delta
    return fresh_alarms

def analize(old_alarms, new_alarms, fresh_alarms, new_values):
    is_state_old_ok = True
    for v in old_alarms.values():
       if v:
           is_state_old_ok = False
           break

    is_state_ok = True
    for v in new_alarms.values():
       if v:
           is_state_ok = False
           break

    is_state_updated = (is_state_old_ok != is_state_ok)

    message_data = dict()
    for id, kv in fresh_alarms.items():
        data = new_values[id].get('value', {})
        name = new_values[id].get('name', '')
        message_data[name] = dict()
        for k in kv:
            message_data[name][k] = data.get(k)

    return is_state_ok, is_state_updated, message_data

def bot_report(last_values, new_values):

    old_alarms = load_alarms(last_values)

    new_alarms = load_alarms(new_values)

    fresh_alarms = get_fresh_alarms(old_alarms, new_alarms)

    is_state_ok, is_state_updated, message_data = analize(old_alarms, new_alarms, fresh_alarms, new_values)

    if is_state_ok:
        text = f'🟢 <b>OK</b>\n'
    else:
        text = f'🔴 <b>ALERT</b>\n'

    for name, kv in message_data.items():
        text += f'<b>{name}</b>:\n'
        for k, v in kv.items():
            text += f' {k}: {v}\n'

    if is_state_updated or message_data:
        bot = TBot()
        bot.send_message(text)

if __name__ == "__main__":
    last_values = {4: {'status': {'tmp': 'Ok'}, 'value': {'tmp': 6.4849853515625e-05}, 'name': 'disk_tmp'}, 2: {'status': {'screen': 'Error'}, 'value': {'screen': 33.87618637084961}, 'name': 'disk_screen'}, 1: {'status': {'used': 'Ok'}, 'value': {'used': 63, 'total': 118}, 'name': 'disk'}, 3: {'status': {'db': 'Ok'}, 'value': {'db': 1.0258369445800781}, 'name': 'disk_db'}}

    new_values = {1: {'name': 'disk', 'status': {'used': None}, 'value': {'total': -1, 'used': -1}}, 2: {'name': 'disk_screen', 'status': {'screen': 'Warning'}, 'value': {'screen': 28.6102294921875}}, 3: {'name': 'disk_db', 'status': {'db': 'Error'}, 'value': {'db': 28.6102294921875}}, 4: {'name': 'disk_tmp', 'status': {'tmp': 'Error'}, 'value': {'tmp': 28.6102294921875}}}
    new_values = {1: {'name': 'disk', 'status': {'used': 'Unhealthy'}, 'value': {'total': -1, 'used': -1}}, 2: {'name': 'disk_screen', 'status': {'screen': 'Warning'}, 'value': {'screen': 28.6102294921875}}, 3: {'name': 'disk_db', 'status': {'db': 'Error'}, 'value': {'db': 28.6102294921875}}, 4: {'name': 'disk_tmp', 'status': {'tmp': 'Error'}, 'value': {'tmp': 28.6102294921875}}}

    bot_report(last_values, new_values)
