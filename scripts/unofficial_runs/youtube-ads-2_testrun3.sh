#!/bin/bash

python main.py True False collect 0 configs/config_swankerie001.json male video_list/science_videos_subset_20230815_0_30_41.csv video_id True 0 3000 True True &
python main.py True False collect 0 configs/config_canarsie001.json male video_list/science_videos_subset_20230815_0_30_41.csv video_id True 0 3000 True False &
python main.py True False collect 0 configs/config_bantamki001.json male video_list/science_videos_subset_20230815_0_30_41.csv video_id True 0 3000 False False