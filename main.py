from get_video_info import get_video_info
from video_controls import *
from utils import *
from get_ad_info import *

import pandas as pd
import json
import time 
import traceback
import os
import sys

from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import NoSuchWindowException

VIDEO_COUNT = 0
AVAILABLE_VIDEO_COUNT = 0
CURRENT_INDEX = 0

def run_video_list(config_path, mode, headless, sleep, video_list, video_id_column_name,
                   start_index, end_index, until_number_of_available_videos, output, log_file):
    global VIDEO_COUNT
    global AVAILABLE_VIDEO_COUNT
    global CURRENT_INDEX
    
    df = pd.read_csv(video_list)
        
    if until_number_of_available_videos:
        end = len(df)
    else:
        end = end_index

    url_list = [
        (df_index,"https://www.youtube.com/watch?v="+ i[video_id_column_name]) for df_index, i in df[start_index:end].iterrows()
    ]

    # create driver and set up activity and ad personalization
    if headless is True or headless == "true":
        headless = True
    else:
        headless = False

    driver = create_driver(config_path, headless=headless, page_load_strategy="normal") 

    # start running through the video list
    for df_index, url in url_list:
        log_file.write(f"{df_index}, {url}\n")

        try:
            video_data = get_video_info(url, driver, mode=mode, sleep=sleep)
            video_data["df_index"] = df_index
            video_data["id"] = VIDEO_COUNT
            video_data["avc"] = AVAILABLE_VIDEO_COUNT

            json.dump(video_data, output, ensure_ascii=True)
            output.write('\n')

            # force write to disk. relatively expensive but data/logs is more important
            output.flush()
            os.fsync(output)

            log_file.flush()
            os.fsync(log_file)

            VIDEO_COUNT += 1
            CURRENT_INDEX += 1

            if "video_title" in video_data and (video_data["video_title"] or video_data["preroll_ad_id"]):
                AVAILABLE_VIDEO_COUNT += 1
            
            if until_number_of_available_videos and AVAILABLE_VIDEO_COUNT == end_index:
                break
            

        except (NoSuchWindowException, WebDriverException) as e:

            log_file.write(traceback.format_exc() + '\n')
            log_file.flush()
            os.fsync(log_file)
            
            log_file.write("Restarting driver \n")
            
            driver.quit()
            run_video_list(config_path, mode, headless, sleep, video_list, video_id_column_name,
                           CURRENT_INDEX, end_index, until_number_of_available_videos, output, log_file)
            break

        except Exception as e:

            log_file.write(traceback.format_exc() + '\n')
            log_file.flush()
            os.fsync(log_file)

    driver.quit()

if __name__ == "__main__":
    start_time = time.time()

    # CHANGE THESE BEFORE RUNNING
    ####################################################################
    running_from_vm = False # on gcp
    headless = False # running without gui
    mode = "collect" # mode is "prime" or "collect"
    sleep = 0 # stay an extra number of seconds per video
    config_path = "configs/config_happysquare88.json" # If no config.json, leave ""
    gender = "male" # "male" or "female"
    video_list = "video_list/us_entertainment_unique_Aug152023.csv"
    video_id_column_name = "video_id"
    until_number_of_available_videos = False # if True, crawl until reach end_index number of available videos
    start_index = 250
    end_index = 252 # end index of video list or number of available videos to crawl
    ad_personalization_on = True
    activity_on = True
    ####################################################################

    args = sys.argv[1:]
    if not args:
        running_from_cmd = False
    else:
        running_from_cmd = True
        args = [a.lower() for a in args]
        running_from_vm = args[0]
        headless = args[1]
        mode = args[2]
        sleep = int(args[3])
        config_path = args[4]
        gender = args[5]
        video_list = args[6]
        video_id_column_name = args[7]
        until_number_of_available_videos = args[8]
        start_index = int(args[9])
        end_index = int(args[10])
        ad_personalization_on = args[11]
        activity_on = args[12]
        

    # Log username and dataset being used
    username = "anonymous"
    if config_path:
        config_f = open(config_path, 'r')
        config = json.load(config_f)
        config_f.close()
        username = config["username"]

    # log_dir = "logs" if running_from_vm else "logs_test"
    # output_dir = "output" if running_from_vm else "output_test"
    dirs = ['logs', 'logs_test', 'output_test', 'output', f"error_screenshots_{username}", f"unavailable_screenshots_{username}"]
    for dir in dirs:
        if not os.path.exists(dir):
            os.makedirs(dir)

    # create driver and set up activity and ad personalization
    driver = create_driver(config_path, headless=False, page_load_strategy="normal") 
    
    if activity_on is True or activity_on == "true":
        turn_on_activity(driver)
        turn_on_youtube_history(driver)
    else:
        turn_off_activity(driver)
        turn_off_youtube_history(driver)
    
    if ad_personalization_on is True or ad_personalization_on == "true":
        turn_off_ad_personalization(driver)
        time.sleep(5)
        turn_on_ad_personalization(driver)
    else:
        turn_off_ad_personalization(driver)

    change_gender(driver, target_gender=gender)
    turn_off_location(driver)
    delete_activity(driver)
    time.sleep(5)
    driver.save_screenshot(f"error_screenshots_{username}/activity_deletion_screen.png")
    driver.quit()

    if running_from_vm is True or running_from_vm == "true":
        log_dir = "logs"
        output_dir = "output"
    else:
        log_dir = "logs_test"
        output_dir = "output_test"

    # generate timestamp to name the log and output file
    test_str = f"{get_test_id()}_{username}"
    log_basename = f"log_{test_str}.txt"
    log_filename = f"{log_dir}/{log_basename}"
    output_basename = f"output_{test_str}.json"
    output_filename = f"{output_dir}/{output_basename}"
    log_file = open(log_filename, "w")
    output = open(output_filename, 'w', encoding='utf-8')
    
    log_file.write(f"Running from cmd: {running_from_cmd} \n")
    log_file.write(f"Using {username} account, {gender} \n")
    log_file.write(f"Using {video_list}[{start_index}:{end_index}], until_available: {until_number_of_available_videos}\n")
    log_file.write(f"Ad personalization on: {ad_personalization_on}, Activity on: {activity_on}\n")
    log_file.write(f"Running on vm: {running_from_vm}, headless: {headless} \n")

    output.write(f"Using {username} account, {gender} \n")
    output.write(f"Using {video_list}[{start_index}:{end_index}], until_available: {until_number_of_available_videos}\n")
    output.write(f"Ad personalization on: {ad_personalization_on}, Activity on: {activity_on}\n")
    output.write(f"Running on vm: {running_from_vm}, headless: {headless} \n")


    # Start collecting data

    CURRENT_INDEX = start_index

    # putting inside a while loop so it can restart after some unexpected bug
    if until_number_of_available_videos:
        while AVAILABLE_VIDEO_COUNT < end_index or VIDEO_COUNT == len(video_list)-1:
            log_file.write("Start using while loop\n")    
            run_video_list(config_path, mode, headless, sleep, video_list, video_id_column_name,
                           CURRENT_INDEX, end_index, until_number_of_available_videos, output, log_file)
    else:
        while VIDEO_COUNT < (end_index-start_index) or VIDEO_COUNT == end_index-1:    
            log_file.write("Start using while loop\n") 
            run_video_list(config_path, mode, headless, sleep, video_list, video_id_column_name,
                           CURRENT_INDEX, end_index, until_number_of_available_videos, output, log_file)

    
        
    output.close()
    log_file.write(f"Finished in {time.time()-start_time}s \n")
    log_file.write("Closing, goodbye")
    log_file.close()


    # clean up after run
    driver = create_driver(config_path, headless=False, page_load_strategy="normal") 
    delete_activity(driver)
    turn_off_ad_personalization(driver)
    driver.quit()


    # Upload log and output to gcp
    project_name = "dontcrimeme"
    bucket_name = "youtube-ads-2023"
    gcp_log_dir = "logs_run4"
    gcp_output_dir = "output_run4"
    source_files = [output_filename,log_filename]
    dest_files = [f"{gcp_output_dir}/{output_basename}", f"{gcp_log_dir}/{log_basename}"]

    for sfile, dfile in zip(source_files, dest_files):
        upload_blob(project_name, bucket_name, sfile, dfile)
