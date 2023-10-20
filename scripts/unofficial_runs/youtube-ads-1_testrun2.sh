#!/bin/bash

python main.py True True collect 0 configs/config_alabaster192.json male news_videos_subset_20230815_0_31_07.csv video_id True 0 3000 True True &
python main.py True True collect 0 configs/config_ponnuki002.json male news_videos_subset_20230815_0_31_07.csv video_id True 0 3000 True False &
python main.py True True collect 0 configs/config_happysquare88.json male news_videos_subset_20230815_0_31_07.csv video_id True 0 3000 False False &

