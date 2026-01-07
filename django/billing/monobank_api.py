import os
import copy
import requests

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

            response = self.get_request(self.key_url, self.cfg[app_id]['TOKEN'])
            self.cfg[app_id]['KEY'] = response['key']

    def mk_monobank_pay(self, app_id, periodicity=None):
        return None

    def get_request(self, url, token):
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-Token": token
        }

        try:
            response = requests.get(url, headers=headers)
        except Exception as err:
            print(err)
            return str(err)
        if response.status_code != 200:
            return f'Error request: {url}'

        return response.json()

    def post_request(self, url, token, data):
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-Token": token
        }

        try:
            response = requests.post(url, headers=headers, json=data)
        except Exception as err:
            print(err)
            return str(err)
        if response.status_code != 200:
            return f'Error request: {url}'

        return 'Ok'


if __name__ == '__main__':
    import environ

    environ.Env.read_env()
    mb = MB()

    ORDER_TABLE = 'billing.orders'
    PAYMENTS_TABLE = 'billing.payments'

    print(mb.cfg)
