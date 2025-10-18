#!/bin/bash

./panel-csv-to-yaml.py --name "openwfs-v2a" --panel-width 250 --panel-height 250 --panel-depth 10 openwfs-panel-layout-v2a.csv
./panel-csv-to-yaml.py --name "openwfs-v1" --panel-width 1050 --panel-height 16 --panel-depth 18 openwfs-panel-layout-v1.csv