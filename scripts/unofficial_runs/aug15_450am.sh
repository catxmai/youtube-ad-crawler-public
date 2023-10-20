#!/bin/bash

python main.py True True collect 0 configs/config_alabaster192.json male news_videos_subset_20230815_0_31_07.csv video_id True 0 3000 True True &
python main.py True True collect 0 configs/config_ponnuki002.json male news_videos_subset_20230815_0_31_07.csv video_id True 0 3000 True False &
python main.py True True collect 0 configs/config_happysquare88.json male news_videos_subset_20230815_0_31_07.csv video_id True 0 3000 False False &
python main.py True True collect 0 configs/config_madcircle001.json male science_videos_subset_20230815_0_30_41.csv video_id True 0 3000 True True &
python main.py True True collect 0 configs/config_tenuki1990.json male science_videos_subset_20230815_0_30_41.csv video_id True 0 3000 True False &
python main.py True True collect 0 configs/config_happysquare89.json male science_videos_subset_20230815_0_30_41.csv video_id True 0 3000 False False &
python main.py True True collect 0 configs/config_canarsie001.json male us_entertainment_unique_Aug152023.csv video_id True 0 3000 True True &
python main.py True True collect 0 configs/config_swankerie001.json male us_entertainment_unique_Aug152023.csv video_id True 0 3000 True False &
python main.py True True collect 0 configs/config_duckystriker.json male us_entertainment_unique_Aug152023.csv video_id True 0 3000 False False &
python main.py True True collect 0 configs/config_bantamki001.json male faddoul_available_Aug152023.csv video_id True 0 3000 True True &
python main.py True True collect 0 configs/config_hoisin001.json male faddoul_available_Aug152023.csv video_id True 0 3000 True False &
python main.py True True collect 0 configs/config_emboxstar.json male faddoul_available_Aug152023.csv video_id True 0 3000 False False