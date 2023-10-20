#!/bin/bash

python main.py True True collect 0 configs/config_madcircle001.json male science_videos_subset_20230815_0_30_41.csv video_id True 0 3000 True True &
python main.py True True collect 0 configs/config_tenuki1990.json male science_videos_subset_20230815_0_30_41.csv video_id True 0 3000 True False &
python main.py True True collect 0 configs/config_happysquare89.json male science_videos_subset_20230815_0_30_41.csv video_id True 0 3000 False False