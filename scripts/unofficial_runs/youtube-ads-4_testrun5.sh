#!/bin/bash

python main.py True False collect 0 configs/config_canarsie001.json male video_list/faddoul_available_Aug152023.csv video_id True 0 3000 True True &
python main.py True False collect 0 configs/config_fearnoduck.json male video_list/faddoul_available_Aug152023.csv video_id True 0 3000 True False &
python main.py True False collect 0 configs/config_miniconvex.json male video_list/faddoul_available_Aug152023.csv video_id True 0 3000 False False