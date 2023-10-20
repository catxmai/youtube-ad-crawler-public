# YouTube Ad Crawler

Collecting ads on YouTube through Selenium. By: Cat Mai, Kyle Spinelli, Cameron Ballard. For questions, email `cat.mai[at]nyu.edu`

Note: This repository is mainly for reference purpose and not meant to run out of the box successfully. 

### Files and Folders

`/analysis` Contains aggregated result files and analysis notebooks

`/scripts` Contains bash files that were used to run the actual experiments

`/video_list` Contains video lists used for crawling ads

`generate_script.ipynb` Generates one-line Python cmd for the crawler

`sandbox.py` Quick tests of the crawler

`output_example.json` Example of output file

`config_example.json` Example of config file for running Selenium while logged in

Main crawler:
- `main.py`
- `utils.py`
- `get_video_info.py`
- `get_ad_info.py`
- `video_controls.py`

### Setup

Note (again): This repository is mainly for reference purpose and not meant to run out of the box successfully. Still, some vital setup steps:

Run `pip install -r requirements.txt`

Download a driver for chrome found here https://chromedriver.chromium.org/downloads. Make sure the driver matches your chrome version (check in Chrome Settings)
Put `chromedriver.exe` in the same folder where `create_driver()` is (currently in `utils.py`)


### Running and Outputs

Change variables in `main.py` to reflect current setup. Most of the info collection is done in `get_video_info()` in `get_video_info.py`. 

Outputs of the program are written in json-like format with multiple dicts per file, each dict represents a video. See `output_example.json`.


