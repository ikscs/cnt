#!/usr/bin/bash
cd /app

./get_order.py

./periodic_runner.py

./periodic_report.py

./sql_call.py "call pcnt.update_demo()"
