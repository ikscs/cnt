#!/usr/local/bin/python
from jinja2 import Template
from weasyprint import HTML
import base64

from grn import grn_text

def to_money(value):
    s = f"{value:,.2f}".replace(',', '&nbsp')
    s = s.replace('.', ',')
    return s

def get_order(cursor, order_id):
    sql = '''SELECT amount, o.currency, description, dt, legal_name,
(SELECT t.order_txt FROM billing.generate_order_txt(customer_id::INTEGER, order_id) AS t)
FROM billing.orders o JOIN public.customer USING(customer_id) WHERE order_id=%s;'''

    cursor.execute(sql, [order_id,])
    row = cursor.fetchone()
    if not row:
        return False, None

    return True, row

def get_template(cursor, table, param):
    p = ' AND '.join([f'"{k}"=%s' for k in param.keys()])
    sql = f"SELECT type AS t, name, content FROM {table}"
    if p:
        sql = f"{sql} WHERE {p}"

    cursor.execute(sql, list(param.values()))

    rows = cursor.fetchall()
    if not rows:
        return False, None

    html = dict()
    png = dict()
    for row in rows:
        t, name, content = row
        if t == 'html':
            html[name] = content.tobytes().decode('utf-8')
        elif t == 'png':
            v = content.tobytes()
            v = base64.b64encode(v).decode('utf-8')
            png[name] = f'data:image/png;base64,{v}'

    if not html:
        return False, None, None

    return True, html, png

def generate_pdf_from_template(html, png, data):
    for k, v in png.items():
        name = k.replace('.', '_')
        html = html.replace(k, f'{{{{ {name} }}}}')
        data[name] = v

    template = Template(html)

    html_content = template.render(**data)

#    with open("output.html", "w", encoding='utf-8') as output_file:
#        output_file.write(html_content)

    output = HTML(string=html_content).write_pdf()
    return output

def create_invoice_data(order_txt, amount, description, dt, legal_name):

    total = round(float(amount), 2)
    vat = round(total*0.2, 2)

    invoice_data = {
        'order_txt': order_txt,
        'description': description,

        'total': to_money(total),
        'total_txt': grn_text(total),

        'vat': to_money(vat),
        'vat_txt': grn_text(vat),

        #'order_date': dt.isoformat(sep=" ", timespec="seconds"),
        'order_date': dt.strftime("%d-%m-%Y"),

        'legal_name': legal_name if legal_name else '',
    }

    return invoice_data

def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

def main_offline():
    from datetime import datetime

    order_id = 108
    row = (4860.05, 'UAH', 'LPR000170008 Доступ до онлайн-сервису розпізнавання автомобільних номерів згідно рахунку № L-0300108 від 25-12-2025', datetime.now(), 'ТОВ «Компанія клієнта»', 'L-0300108')

    amount, currency, description, dt, legal_name, order_txt = row

    with open("template.html", "rt", encoding='utf-8') as f:
        html = f.read()

    png = dict()
    for k in ['stamp.png', 'sign.png', 'logo.png']:
        png[k] = f'data:image/png;base64,{get_base64_image(k)}'

    invoice_data = create_invoice_data(order_txt, amount, description, dt, legal_name)

    output_pdf = generate_pdf_from_template(html=html, png=png, data=invoice_data)

    with open('output_invoice.pdf', 'wb') as f:
        f.write(output_pdf)
        print(f"PDF generated successfully")

def main():
    from db_wrapper import DB
    order_id = 108

    db = DB()
    db.open()

    output_pdf = print_order(order_id, db.cursor)

    db.close()

    with open('output_invoice.pdf', 'wb') as f:
        f.write(output_pdf)
        print(f"PDF generated successfully")

def print_order(order_id, cursor):
    result, row = get_order(cursor, order_id)
    if not result:
        return None

    amount, currency, description, dt, legal_name, order_txt = row

    result, html, png = get_template(cursor, 'billing.invoice_template', {'currency': currency})
    if not result:
        return None

    invoice_data = create_invoice_data(order_txt, amount, description, dt, legal_name)

    output_pdf = generate_pdf_from_template(html=html['template'], png=png, data=invoice_data)

    return output_pdf

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    main()
    #main_offline()
