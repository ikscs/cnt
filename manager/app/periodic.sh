#!/usr/bin/bash
cd /app

./get_order.py
#./get_du.py
./periodic_runner.py

./sql_call.py "call pcnt.update_demo()"
