import os
from liqpay import LiqPay

class LP():
    app_ids = dict()
    cfg = dict()
    params = dict()
    params_default = {
        'action': 'pay',
        'amount': '0.01',
        'currency': 'USD',
        'description': '',
        'order_id': 0,
        'version': '3',
    }

    def __init__(self):
        ids = os.environ.get('LIQPAY_APP_IDS', '').split(',')
        for n, e in enumerate(ids, 1):
            self.app_ids[n] = e
            self.params[e] = self.params_default.copy()
            self.cfg[e] = dict()

        for k, v in os.environ.items():
            for n, app_id in self.app_ids.items():
                key = f'LIQPAY{n}_'
                if k.startswith(key):
                    k = k.split('_', 1)[-1]
                    self.cfg[app_id][k] = v

        for app_id in self.app_ids.values():
            self.params[app_id]['sandbox'] = self.cfg[app_id]['SANDBOX']
            self.params[app_id]['server_url'] = self.cfg[app_id]['CALLBACK']
            url = self.cfg[app_id].get('RESULT_URL')
            if url:
                self.params[app_id]['result_url'] = url

    def mk_liqpay(self, app_id):
        liqpay = LiqPay(self.cfg[app_id]['PUBLIC_KEY'], self.cfg[app_id]['PRIVATE_KEY'])
        return liqpay

if __name__ == '__main__':
    import environ

    environ.Env.read_env()
    lp = LP()

    ORDER_TABLE = 'billing.orders'
    PAYMENTS_TABLE = 'billing.payments'

    print(lp.cfg)
