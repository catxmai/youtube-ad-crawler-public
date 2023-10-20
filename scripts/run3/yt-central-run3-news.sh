#!/bin/bash

python main.py True False collect 0 configs/config_affineroot.json male video_list/news_subset_Sep212023.csv video_id True 0 3000 True True &
python main.py True False collect 0 configs/config_clopentopo.json male video_list/news_subset_Sep212023.csv video_id True 0 3000 True False &
python main.py True False collect 0 configs/config_kahlerform.json male video_list/news_subset_Sep212023.csv video_id True 0 3000 False False