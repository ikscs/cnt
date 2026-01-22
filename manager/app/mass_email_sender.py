#!/usr/local/bin/python
import json
from datetime import datetime
from jinja2 import Template

from db_wrapper import DB
from print_order import print_order, get_template
from make_reaction import get_sender

class Email_template():
    data = dict()

    def __init__(self, cursor):
        self.cursor = cursor

    def get(self, lang):
        if lang not in self.data:
            result, html, png = get_template(self.cursor, 'public.email_template', {'lang': lang})
            self.data[lang] = (result, html, png)
        return self.data[lang]

def create_template_data(legal_name, dt, unsubscribe_uuid):
    invoice_data = {
        'legal_name': legal_name if legal_name else '',
        'unsubscribe_uuid': unsubscribe_uuid,
        'order_date': dt.strftime("%d-%m-%Y"),
    }
    return invoice_data

def generate_html_from_template(html, png, data):
    if 'body' in html:
        body = html['body']
        for k, v in png.items():
            name = k.replace('.', '_')
            body = body.replace(k, f'{{{{ {name} }}}}')
            data[name] = v
        html['body'] = body

    html_content = dict()
    for k, v in html.items():
        template = Template(v)
        html_content[k] = template.render(**data)

    return html_content

def main():

    dt_now = datetime.now()

    db = DB()
    db.open()

    #UPDATE ext
    sql_update_ext = '''INSERT INTO public.customer_ext (customer_id) SELECT customer_id FROM public.customer ON CONFLICT(customer_id) DO NOTHING'''
    db.cursor.execute(sql_update_ext)
    db.conn.commit()

    #SELECT desired tasks
    sql_email_list = '''SELECT customer_id, legal_name, c.lang, c.currency, email, order_count, unsubscribe_uuid
FROM public.customer c
LEFT JOIN public.customer_ext e USING(customer_id)
LEFT JOIN lpr.lpr_order o USING(customer_id)
LEFT JOIN billing.balance b USING(customer_id)
WHERE 1=1
AND email_enabled
AND email IS NOT NULL
AND o.analytics_type=1
AND NOW() >= last_email_dt + INTERVAL '3 days'
AND (NOW() BETWEEN b.end_date - INTERVAL '1 day' AND b.end_date)
'''

    sql_update_email_dt = '''UPDATE public.customer_ext SET last_email_dt=NOW() WHERE customer_id=%s;'''

    sql_create_order = '''SELECT billing.create_order((SELECT value FROM lpr.subscription_base_price WHERE crn=%s), %s, 'Remind order', 'lpr', 'bank', %s);'''

    #EMAIL
    result, sender = get_sender(db.cursor)
    if not result:
        print('Error:', sender)
        db.close()
        exit()

    email_template = Email_template(db.cursor)

    db.cursor.execute(sql_email_list)
    for row in db.cursor.fetchall():
        customer_id, legal_name, lang, currency, email, order_count, unsubscribe_uuid = row
        param = {'cameras': order_count, 'currency': currency, 'periodMon': 1, 'origin': 'email scheduler'}

        #Create new order
        db.cursor.execute(f"SET app.customer_id TO '{customer_id}';")
        db.cursor.execute(sql_create_order, [currency, currency, json.dumps(param)])
        result = db.cursor.fetchone()
        if not result:
            continue
        order_id = result[0]

        #Make pdf order
        pdf_order = print_order(order_id, db.cursor)
        if not pdf_order:
            continue

        #Load email template
        result, html, png = email_template.get(lang)
        if not result:
            continue

        #Generate data
        data = create_template_data(legal_name, dt_now, unsubscribe_uuid)

        #Create letter data
        result_html = generate_html_from_template(html, png, data)

        #Just send
        sender.recipient = email
        sender.send_email(subject=result_html['subject'], body=None, html=result_html['body'], attachment_data=pdf_order, attachment_name=f'invoice_{order_id}.pdf')

        #Update datetime
        db.cursor.execute(sql_update_email_dt, [customer_id, ])

    db.close()

if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()
    main()
