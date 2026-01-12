import os
import copy
import requests
import base64
import hashlib
import ecdsa

class MB():
    app_ids = dict()
    cfg = dict()
    params = dict()
    params_default = {
        'amount': '0.01',
        'ccy': 980,
        'merchantPaymInfo': {'reference': 0, 'destination': ''},
    }
    base = 'https://api.monobank.ua'
    invoice_url = f'{base}/api/merchant/invoice/create'
    subscribe_url = f'{base}/api/merchant/subscription/create'
    key_url = f'{base}/api/merchant/pubkey'
    status_url = f'{base}/api/merchant/invoice/status?invoiceId='
    subscription_url = f'{base}/api/merchant/subscription/status?subscriptionId='
    subscription_remove_url = f'{base}/api/merchant/subscription/remove'

    def __init__(self):
        ids = os.environ.get('MONOBANK_APP_IDS', '').split(',')
        for n, e in enumerate(ids, 1):
            self.app_ids[n] = e
            self.params[e] = copy.deepcopy(self.params_default)
            self.cfg[e] = dict()

        for k, v in os.environ.items():
            for n, app_id in self.app_ids.items():
                key = f'MONOBANK{n}_'
                if k.startswith(key):
                    k = k.split('_', 1)[-1]
                    self.cfg[app_id][k] = v

        for app_id in self.app_ids.values():
            self.params[app_id]['redirectUrl'] = self.cfg[app_id]['REDIRECT_URL']
            self.params[app_id]['successUrl'] = self.cfg[app_id]['SUCCESS_URL']
            self.params[app_id]['failUrl'] = self.cfg[app_id]['FAIL_URL']
            self.params[app_id]['webHookUrl'] = self.cfg[app_id]['WEBHOOK_URL']
            self.params[app_id]['webHookUrls'] = {'chargeUrl': self.cfg[app_id]['CHARGE_URL'], 'statusUrl': self.cfg[app_id]['STATUS_URL'],}

            try:
                response = self.get_request(self.key_url, self.cfg[app_id]['TOKEN'])
                #self.cfg[app_id]['KEY'] = response['key']
                pub_key_bytes = base64.b64decode(response['key'])
                self.cfg[app_id]['KEY'] = ecdsa.VerifyingKey.from_pem(pub_key_bytes.decode())
            except Exception as err:
                print(str(err))

    def verify_signature(self, app_id, body_bytes, signature_str):
        signature_bytes = base64.b64decode(signature_str)
        try:
            ok = self.cfg[app_id]['KEY'].verify(signature_bytes, body_bytes, sigdecode=ecdsa.util.sigdecode_der, hashfunc=hashlib.sha256)
        except Exception as err:
            print(str(err))
            return False
        if ok:
            return True
        return False

    def mk_monobank_pay(self, app_id, periodicity=None):
        return None

    def get_request(self, url, token):
        headers = {"Accept": "application/json", "Content-Type": "application/json", "X-Token": token}
        try:
            response = requests.get(url, headers=headers)
        except Exception as err:
            print(err)
            return str(err)
        if response.status_code != 200:
            return f'Error request: {url}'

        return response.json()

    def post_request(self, url, token, data):
        headers = {"Accept": "application/json", "Content-Type": "application/json", "X-Token": token}
        try:
            response = requests.post(url, headers=headers, json=data)
        except Exception as err:
            print(err)
            return str(err)
        if response.status_code != 200:
            return f'Error request: {url}'

        try:
            return response.json()
        except Exception as err:
            print(err)
            return str(err)

    def post_200(self, url, token, data):
        headers = {"Accept": "application/json", "Content-Type": "application/json", "X-Token": token}
        try:
            response = requests.post(url, headers=headers, json=data)
        except Exception as err:
            print(err)
            return {'errCode': 'ERROR', 'errText': str(err)}
        if response.status_code == 200:
            return {'errCode': 'OK', 'errText': 'Ok'}

        try:
            result = response.json()
        except Exception as err:
            print(err)
            return {'errCode': 'ERROR', 'errText': str(err)}

        return {'errCode': result.get('errCode', 'UNKNOWN'), 'errText': result.get('errText', '')}

    def get_monobank_subscription_state(self, app_id, subscription_id):
        try:
            token = self.cfg[app_id]['TOKEN']
        except Exception as err:
            print(err)
            return f'Token not found for {app_id}'

        result = self.get_request(f'{self.subscription_url}{subscription_id}', token)
        return result

    def monobank_subscription_remove(self, app_id, subscription_id):
        try:
            token = self.cfg[app_id]['TOKEN']
        except Exception as err:
            print(err)
            return {'errCode': 'ERROR', 'errText': f'Token not found for {app_id}'}

        result = self.post_200(self.subscription_remove_url, token, {'subscriptionId': subscription_id})
        return result

if __name__ == '__main__':
    import environ

    environ.Env.read_env()
    mb = MB()

    print(mb.cfg)
