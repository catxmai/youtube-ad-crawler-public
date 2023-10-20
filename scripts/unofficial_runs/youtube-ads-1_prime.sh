#!/bin/bash

python main.py True False prime 120 configs/config_hoisin001.json male video_list/us_entertainment_unique_Aug152023.csv video_id True 0 1000 True True &
python main.py True False prime 120 configs/config_emboxstar.json male video_list/us_entertainment_unique_Aug152023.csv video_id True 0 1000 True True &
python main.py True False prime 120 configs/config_bantamki001.json male video_list/us_entertainment_unique_Aug152023.csv video_id True 0 1000 True True