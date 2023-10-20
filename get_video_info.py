import re
import time
import json

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import *
from get_ad_info import *
from video_controls import *

from utils import *


def get_video_info(video_url, driver, mode="collect", sleep=0) -> dict:
    """
    Parameters
    ----------
    driver: a selenium webdriver object (should be pointed at a YouTube video)
    mode: "prime" (not collecting ads) or "collect"
    sleep: extra sleep time per video (in seconds)

    Returns
    -------
    video_data: a dict of info and stats for the current video

    """
    if not driver:
        return
    
    driver.get(video_url)
    time.sleep(.5)

    video_id = get_video_id(driver.current_url)
    username = get_username(driver)

    if mode == "collect":
        try:
            play_video(driver)
        except NoSuchElementException:
            
            driver.save_screenshot(f"unavailable_screenshots_{username}/{video_id}.png")
            return {
                'video_id': video_id,
                'video_unavailable': True
            }
        except ElementNotInteractableException:

            try:
                driver.find_element(By.CSS_SELECTOR, "#player-error-message-container, .ytp-error-content-wrap-reason")
                driver.save_screenshot(f"unavailable_screenshots_{username}/uninteractable_{video_id}.png")
                return {
                    'video_id': video_id,
                    'video_uninteractable': True
                }
            except NoSuchElementException:
                driver.save_screenshot(f"unavailable_screenshots_{username}/loading_{video_id}.png")
                print(f"{username}: driver in loading state, video_id: {video_id}")

        return _collect_video(driver, sleep=sleep)
    

    if mode == "prime":
        try:
            play_video(driver)
        except:
            
            driver.save_screenshot(f"unavailable_screenshots_{username}/{video_id}.png")
            return {
                'video_id': video_id,
                'video_unavailable': True
            }
        
        return _prime_video(driver, sleep=sleep)



def _prime_video(driver, sleep):

    video_id = get_video_id(driver.current_url)
    time.sleep(5)
    load_script_tag(driver)
    video_title = get_video_title()
    channel_name = get_channel_name()
    # video_description = get_video_description()
    date_uploaded = get_upload_date()
    # likes = get_likes(driver)
    # views = get_views()
    # comment_count = get_comment_count(driver)
    # video_genre = get_video_genre()
    # channel_id = get_channel_id(driver)
    video_url = "https://www.youtube.com/watch?v=" + video_id

    time.sleep(sleep)

    video_data = {
        'video_id': video_id,
        'video_title': video_title,
        'video_url': video_url,
        'channel_name': channel_name,
        # 'channel_id': channel_id,
        # 'video_genre': video_genre,
        # 'video_description': video_description,
        'date_uploaded': date_uploaded,
        # 'likes': likes,
        # 'views': views,
        # 'comment_count': comment_count,
    }

    return video_data

def _collect_video(driver, sleep):

    username = get_username(driver)
    video_id = get_video_id(driver.current_url)
    time.sleep(.5)
    pause_video(driver)

    preroll_ad_id, preroll_ad_reasons, preroll_ad_info, \
    preroll_ad_site, preroll_ad_card, preroll_ad_duration = None, None, None, None, None, None
    time.sleep(.5)

    ad_order = 0
    preroll_ad_id = get_preroll_ad_id(driver)
    if preroll_ad_id == video_id or not preroll_ad_id:
        preroll_ad_id = None
    else:
        try:
            preroll_ad_reasons, preroll_ad_info = get_preroll_ad_info(driver)
            preroll_ad_site, preroll_ad_card = get_preroll_ad_site(driver)
            preroll_ad_duration = get_ad_duration(driver)
        except IframeExitException:
            switch_back(driver)

        ad_order = 1
        try:
            ad_order = get_ad_order(driver)
            if ad_order == 2:
                timestamp = get_test_id()
                driver.save_screenshot(f"error_screenshots_{username}/missed_ad1_{timestamp}_{video_id}.png")
        except:
            pass

    # extracting second ad by waiting for the first one to finish. Real-time buffer period between ad varies although it's a fixed number
    MAX_WAIT_TIME = 600 
    BUFFER_AD_TIME = 2
    preroll_ad2_id, preroll_ad2_reasons, preroll_ad2_info, \
    preroll_ad2_site, preroll_ad2_card, preroll_ad2_duration = None, None, None, None, None, None

    num_ads_left = get_number_of_ads_left(driver)
    has_more_than_two_ads = True if num_ads_left > 1 else False

    if num_ads_left == 1 or get_preroll_ad_id(driver) == "empty_video" or ad_order == 2:
        if ad_order == 1:
            time_left = get_ad_duration(driver)
            if time_left < MAX_WAIT_TIME:

                play_video(driver)
                time.sleep(time_left + BUFFER_AD_TIME)

                # managing varying buffer time because of system
                current_video_id = get_preroll_ad_id(driver)
                while current_video_id in ["", "empty_video", preroll_ad_id, None]:
                    time.sleep(2)
                    current_video_id = get_preroll_ad_id(driver)
                    if current_video_id == video_id:
                        break

        preroll_ad2_id = get_preroll_ad_id(driver)
        if preroll_ad2_id in [video_id, preroll_ad_id, "empty_video", "", None]:
            preroll_ad2_id = None
        else:
            pause_video(driver)
            preroll_ad2_reasons, preroll_ad2_info = get_preroll_ad_info(driver)
            preroll_ad2_site, preroll_ad2_card = get_preroll_ad_site(driver)
            preroll_ad2_duration = get_ad_duration(driver)
    
    if sleep > 0:
        skip_ad(driver)
        time.sleep(sleep)
        pause_video(driver)

    load_script_tag(driver)
    video_title = get_video_title()

    side_ad_site = get_side_ad_site(driver)
    side_ad_img = get_side_ad_img(driver)
    if side_ad_site or side_ad_img:
        side_ad_reasons, side_ad_info = get_side_ad_info(driver)
        side_ad_text = get_side_ad_text(driver)
        
    else:
        side_ad_reasons, side_ad_info, side_ad_text = None, None, None

    channel_name = get_channel_name()
    # video_description = get_video_description()
    date_uploaded = get_upload_date()
    likes = get_likes(driver)
    views = get_views()
    # comment_count = get_comment_count(driver)
    video_genre = get_video_genre()
    # channel_id = get_channel_id(driver)

    video_url = "https://www.youtube.com/watch?v=" + video_id
    preroll_ad_video_url = "https://www.youtube.com/watch?v=" + preroll_ad_id if preroll_ad_id else None
    preroll_ad2_video_url = "https://www.youtube.com/watch?v=" + preroll_ad2_id if preroll_ad2_id else None

    promoted_video_title = get_promoted_video_title(driver)
    if promoted_video_title:
        promoted_video_channel = get_promoted_video_channel(driver)
        promoted_video_reasons, promoted_video_info = get_promoted_video_info(driver)
        promoted_video_url = get_promoted_video_url(driver)
    else:
        promoted_video_channel, promoted_video_reasons, promoted_video_info, promoted_video_url = None, None, None, None

    video_data = {
        'video_id': video_id,
        'video_title': video_title,
        'video_url': video_url,
        'channel_name': channel_name,
        # 'channel_id': channel_id,
        'video_genre': video_genre,
        # 'video_description': video_description,
        'date_uploaded': date_uploaded,
        'likes': likes,
        'views': views,
        # 'comment_count': comment_count,

        'has_more_than_two_ads': has_more_than_two_ads,

        'preroll_ad_id': preroll_ad_id,
        'preroll_ad_video_url': preroll_ad_video_url,
        'preroll_ad_duration': preroll_ad_duration,
        'preroll_ad_site': preroll_ad_site,
        'preroll_ad_card': preroll_ad_card,
        'preroll_ad_reasons': preroll_ad_reasons,
        'preroll_ad_info': preroll_ad_info,

        'preroll_ad2_id': preroll_ad2_id,
        'preroll_ad2_video_url': preroll_ad2_video_url,
        'preroll_ad2_duration': preroll_ad2_duration,
        'preroll_ad2_site': preroll_ad2_site,
        'preroll_ad2_card': preroll_ad2_card,
        'preroll_ad2_reasons': preroll_ad2_reasons,
        'preroll_ad2_info': preroll_ad2_info,
        
        'side_ad_site': side_ad_site,
        'side_ad_text': side_ad_text,
        'side_ad_img': side_ad_img,
        'side_ad_reasons': side_ad_reasons, 
        'side_ad_info': side_ad_info,

        'promoted_video_title': promoted_video_title,
        'promoted_video_url': promoted_video_url,
        'promoted_video_channel': promoted_video_channel,
        'promoted_video_reasons': promoted_video_reasons,
        'promoted_video_info': promoted_video_info,
        
    }

    return video_data


def load_script_tag(driver: webdriver.Chrome):
    # loads a web element with id = "scriptTag" that contains a lot of useful info
    global SCRIPT_TAG
    try:
        time.sleep(1)
        SCRIPT_TAG = json.loads(driver.find_element(By.ID, "scriptTag").get_attribute("innerHTML"))
    except NoSuchElementException:
        SCRIPT_TAG = None


def get_video_title():
    try:
        title = SCRIPT_TAG['name']
        return title
    except (TypeError, KeyError) as e:
        return None
    

def get_views():
    try:
        views = SCRIPT_TAG['interactionCount']
        return int(views)
    except (TypeError, KeyError) as e:
        return None
    

def get_channel_name():
    try:
        name = SCRIPT_TAG['author']
        return name
    except (TypeError, KeyError) as e:
        return None
    

def get_video_description():
    try:
        description = SCRIPT_TAG['description']
        return description
    except (TypeError, KeyError) as e:
        return None
    

def get_upload_date():
    try:
        date = SCRIPT_TAG['uploadDate']
        return date
    except (TypeError, KeyError) as e:
        return None
    

def get_video_genre():
    try:
        genre = SCRIPT_TAG['genre']
        return genre
    except (TypeError, KeyError) as e:
        return None
    


def get_channel_id(driver):

    try:
        container = driver.find_element(
            By.CSS_SELECTOR, ".ytp-ce-channel-title.ytp-ce-link.style-scope.ytd-player")
        channel_url = container.get_attribute('href')
        pattern = r"(?<=\/channel\/).{24}"
        match = re.search(pattern, channel_url)

        if match:
            channel_id = match[0] 
    except NoSuchElementException:
        return None

    return channel_id


def get_comment_count(driver):
    # Comment count is not searchable in html element if don't scroll down
    # based on https://stackoverflow.com/questions/22702277/crawl-site-that-has-infinite-scrolling-using-python/60336607#60336607

    SCROLL_PAUSE_TIME = .5

    last_height = driver.execute_script("return document.documentElement.scrollHeight")
    found = False
    container = None

    # Sometimes need to scroll page to get comment section to load
    count = 0
    while not found:
        try:
            container = driver.find_element(By.XPATH, '//yt-formatted-string[@class="count-text style-scope ytd-comments-header-renderer"]')
            found = True
        except:
            found = False

        if not found:
            driver.execute_script("window.scrollTo(0, " + str(last_height/4) + ");")
            time.sleep(SCROLL_PAUSE_TIME)

            # Calculate new scroll height and compare with last scroll height
            new_height = driver.execute_script("return document.documentElement.scrollHeight") 

            if (new_height == last_height) and count > 3:
                driver.execute_script("window.scrollTo(0, 0);")
                return None
            last_height = new_height

        count += 1


    try:
        comment_count = int("".join(list(filter(str.isdigit, container.text))))
    except:
        comment_count = None

    driver.execute_script("window.scrollTo(0, 0);")

    return comment_count


def get_likes(driver):

    # Like button's aria-label is "like this video along with 282,068 other people"
    try:
        like_button_container = driver.find_element(
            By.CSS_SELECTOR, "#segmented-like-button > ytd-toggle-button-renderer > yt-button-shape > button")
        aria_label = like_button_container.get_attribute('aria-label')
        aria_label = aria_label.replace(',', '')
        like_count = int(re.findall('\d+', aria_label)[0])
    except:
        return None

    return like_count