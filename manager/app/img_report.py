import matplotlib.pyplot as plt
from datetime import datetime
from io import BytesIO

def mk_img_report(chart, title_text, data_in):
    chart_type = chart.get('type')
    if chart_type not in ('linear', 'circular'):
        return None
    x_label = chart.get('x_axis_label', '')
    y_label = chart.get('y_axis_label', '')

    try:
        k = chart['x_axis']['field']
        v = chart['body_fields'][0]
    except Exception as err:
        return None

    data = {e.get(k): e.get(v) for e in data_in}

    if chart_type == "linear":
        plt.figure(figsize=(12, 6))
        plt.plot(data.keys(), data.values(), marker='o')
        plt.grid(True, linestyle='--', alpha=0.5)

        plt.title(title_text, fontsize=16)

        plt.xlabel(x_label, fontsize=12)
        plt.ylabel(y_label, fontsize=12)
        plt.grid(True)

        plt.xticks(rotation=90)
        plt.tight_layout()

    elif chart_type == "circular":

        plt.figure(figsize=(10, 8))
        labels = list(data.keys())
        sizes = list(data.values())
        labels = [f'{l:<10}{s:>10}' for l, s in zip(labels, sizes)]

        patches, texts, autotexts = plt.pie(sizes, autopct='%1.1f%%', startangle=140, shadow=False, wedgeprops=dict(width=0.5), pctdistance=1.1)

        plt.legend(patches, labels, loc='lower left')

        plt.title(title_text, fontsize=20)

        plt.axis('equal')

    output = BytesIO()
    plt.savefig(output)
    return output.getbuffer()

if __name__ == '__main__':
    title_text = 'Subject'

    chart = {"type": "circular", "x_axis": {"field": "gender"}, "y_axis": {"field": ""}, "body_fields": ["rate"]}
    data = [{"gender": "Чоловіки", "rate": 33.6}, {"gender": "Жінки", "rate": 66.4}]

    chart = {"type": "linear", "x_axis": {"field": "dd"}, "body_fields": ["cnt"], "y_axis_label": "Liczba odwiedzających", "y_axis": {"field": "name"}}
    data = [{"name": "Sezon", "dd": "2025-06-10", "dd0": "2025-06-10", "point_id": 5, "cnt": 160}, {"name": "Sezon", "dd": "2025-06-11", "dd0": "2025-06-11", "point_id": 5, "cnt": 168}, {"name": "Sezon", "dd": "2025-06-12", "dd0": "2025-06-12", "point_id": 5, "cnt": 152}, {"name": "Sezon", "dd": "2025-06-13", "dd0": "2025-06-13", "point_id": 5, "cnt": 163}, {"name": "Sezon", "dd": "2025-06-14", "dd0": "2025-06-14", "point_id": 5, "cnt": 242}, {"name": "Sezon", "dd": "2025-06-15", "dd0": "2025-06-15", "point_id": 5, "cnt": 298}, {"name": "Sezon", "dd": "2025-06-16", "dd0": "2025-06-16", "point_id": 5, "cnt": 182}, {"name": "Sezon", "dd": "2025-06-17", "dd0": "2025-06-17", "point_id": 5, "cnt": 157}, {"name": "Sezon", "dd": "2025-06-18", "dd0": "2025-06-18", "point_id": 5, "cnt": 176}, {"name": "Sezon", "dd": "2025-06-19", "dd0": "2025-06-19", "point_id": 5, "cnt": 185}, {"name": "Sezon", "dd": "2025-06-20", "dd0": "2025-06-20", "point_id": 5, "cnt": 150}, {"name": "Sezon", "dd": "2025-06-21", "dd0": "2025-06-21", "point_id": 5, "cnt": 215}, {"name": "Sezon", "dd": "2025-06-22", "dd0": "2025-06-22", "point_id": 5, "cnt": 214}, {"name": "Sezon", "dd": "2025-06-23", "dd0": "2025-06-23", "point_id": 5, "cnt": 126}, {"name": "Sezon", "dd": "2025-06-24", "dd0": "2025-06-24", "point_id": 5, "cnt": 125}, {"name": "Sezon", "dd": "2025-06-25", "dd0": "2025-06-25", "point_id": 5, "cnt": 128}, {"name": "Sezon", "dd": "2025-06-26", "dd0": "2025-06-26", "point_id": 5, "cnt": 120}, {"name": "Sezon", "dd": "2025-06-27", "dd0": "2025-06-27", "point_id": 5, "cnt": 91}, {"name": "Sezon", "dd": "2025-06-28", "dd0": "2025-06-28", "point_id": 5, "cnt": 153}, {"name": "Sezon", "dd": "2025-06-29", "dd0": "2025-06-29", "point_id": 5, "cnt": 124}, {"name": "Sezon", "dd": "2025-06-30", "dd0": "2025-06-30", "point_id": 5, "cnt": 78}, {"name": "Sezon", "dd": "2025-07-01", "dd0": "2025-07-01", "point_id": 5, "cnt": 135}, {"name": "Sezon", "dd": "2025-07-02", "dd0": "2025-07-02", "point_id": 5, "cnt": 105}, {"name": "Sezon", "dd": "2025-07-03", "dd0": "2025-07-03", "point_id": 5, "cnt": 59}, {"name": "Sezon", "dd": "2025-07-04", "dd0": "2025-07-04", "point_id": 5, "cnt": 144}, {"name": "Sezon", "dd": "2025-07-05", "dd0": "2025-07-05", "point_id": 5, "cnt": 191}, {"name": "Sezon", "dd": "2025-07-06", "dd0": "2025-07-06", "point_id": 5, "cnt": 195}, {"name": "Sezon", "dd": "2025-07-07", "dd0": "2025-07-07", "point_id": 5, "cnt": 156}, {"name": "Sezon", "dd": "2025-07-08", "dd0": "2025-07-08", "point_id": 5, "cnt": 117}, {"name": "Sezon", "dd": "2025-07-09", "dd0": "2025-07-09", "point_id": 5, "cnt": 116}]

    result = mk_img_report(chart, title_text, data)

    with open(f'{title_text}.png', 'wb') as f:
        f.write(result)
