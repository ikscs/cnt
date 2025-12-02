def adapt_tyto(action, answer):
    result = {'result': False}
    if action == 'check':
        try:
            result['result'] = bool(answer['result'] == 'success')
        except Exception as err:
            pass

    elif action == 'get':
        try:
            result['plates'] = answer['data']['PlatesId']
            result['result'] = True
        except Exception as err:
            pass

    elif action == 'info':
        try:
            info = answer['data']['PlateInfo']
            result['info'] = [{'id': e['Id'], 'brand': e['CarBrand'], 'owner': e['Owner']} for e in info]
            result['result'] = True
        except Exception as err:
            pass

    elif action in ['add', 'modify', 'remove']:
        try:
            result[action] = answer['data']['Count']
            result['result'] = True
        except Exception as err:
            pass

    elif action == 'sync':
        try:
            result['add'] = answer['data']['add']
            result['remove'] = answer['data']['remove']
            result['result'] = True
        except Exception as err:
            pass

    return result


def adapt_action(vendor, action, answer):
    if vendor not in ['Tyto', ]:
        return answer

    if not answer or not isinstance(answer, dict):
        return {'result': False}

    if vendor == 'Tyto':
        return adapt_tyto(action, answer)

    return {'result': False}
