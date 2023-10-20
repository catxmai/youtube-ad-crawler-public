import re
import pandas as pd
import json
import csv

from utils import *
from get_video_info import *



if __name__ == "__main__":

	# project_name = "dontcrimeme"
	# bucket_name = "youtube-ads-2023"
	# upload_from_directory(project_name, bucket_name, "logs_testrun2/", "logs_testrun2/")

	driver = create_driver("config_happysquare88.json", headless=False)
	turn_on_activity(driver)
	turn_on_youtube_history(driver)
	turn_off_ad_personalization(driver)
    
	time.sleep(3)
	
	turn_off_youtube_history(driver)
	turn_on_ad_personalization(driver)
    
	change_gender(driver, target_gender="male")
	turn_off_location(driver)
	delete_activity(driver)

	driver.get("https://www.youtube.com/watch?v=vAhVciDvdjI")
	time.sleep(10)

	driver.get("https://chrome.google.com/sync?otzr=1")
	time.sleep(10)

