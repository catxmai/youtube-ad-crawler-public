#!/bin/bash

python main.py True True collect 0 configs/config_bantamki001.json male faddoul_available_Aug152023.csv video_id True 0 3000 True True &
python main.py True True collect 0 configs/config_hoisin001.json male faddoul_available_Aug152023.csv video_id True 0 3000 True False &
python main.py True True collect 0 configs/config_emboxstar.json male faddoul_available_Aug152023.csv video_id True 0 3000 False False

