#!/bin/bash

python main.py True False collect 0 configs/config_banachnorm.json male video_list/news_subset_Sep192023.csv video_id True 0 3000 True True &
python main.py True False collect 0 configs/config_nonconcave.json male video_list/news_subset_Sep192023.csv video_id True 0 3000 True False &
python main.py True False collect 0 configs/config_sublinears.json male video_list/news_subset_Sep192023.csv video_id True 0 3000 False False