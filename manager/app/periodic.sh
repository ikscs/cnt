#!/usr/bin/bash
cd /app

./get_order.py
#./get_du.py
./periodic_runner.py

