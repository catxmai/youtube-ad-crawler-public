#!/bin/bash

python main.py True False prime 120 configs/config_canarsie001.json male video_list/us_entertainment_unique_Aug152023.csv video_id True 0 1000 True True &
python main.py True False prime 120 configs/config_fearnoduck.json male video_list/us_entertainment_unique_Aug152023.csv video_id True 0 1000 True True &
python main.py True False prime 120 configs/config_madcircle001.json male video_list/us_entertainment_unique_Aug152023.csv video_id True 0 1000 True True