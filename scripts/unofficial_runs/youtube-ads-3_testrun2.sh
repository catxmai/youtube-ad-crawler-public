#!/bin/bash

python main.py True True collect 0 configs/config_canarsie001.json male us_entertainment_unique_Aug152023.csv video_id True 0 3000 True True &
python main.py True True collect 0 configs/config_swankerie001.json male us_entertainment_unique_Aug152023.csv video_id True 0 3000 True False &
python main.py True True collect 0 configs/config_duckystriker.json male us_entertainment_unique_Aug152023.csv video_id True 0 3000 False False
