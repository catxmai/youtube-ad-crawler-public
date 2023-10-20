#!/bin/bash

python main.py False False collect 0 configs/config_catmaimx.json male video_list/faddoul_available_Aug152023.csv video_id True 0 3000 True True &
python main.py False False collect 0 configs/config_happysquare88.json male video_list/faddoul_available_Aug152023.csv video_id True 0 3000 True False &
python main.py False False collect 0 configs/config_happysquare89.json male video_list/faddoul_available_Aug152023.csv video_id True 0 3000 False False
