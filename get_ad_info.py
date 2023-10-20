import time
import re
from utils import *
from video_controls import *

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import *
from selenium.webdriver import ActionChains

class IframeExitException(Exception):
    pass


def get_ad_duration(driver) -> int:

    try:
        time_left_element = driver.find_element(
            By.CSS_SELECTOR, "span.ytp-ad-duration-remaining > div.ytp-ad-text"
        )
    except NoSuchElementException:
        return -1

    time_units = time_left_element.text.split(":")
    time_units.reverse()
    time_left = 0

    for index, value in enumerate(time_units):
        time_left = time_left + int(value)*60**index

    return time_left

def get_number_of_ads_left(driver) -> int:

    try:
        ad_text = driver.find_element(By.CSS_SELECTOR, ".ytp-ad-simple-ad-badge > .ytp-ad-text").get_attribute("innerHTML")
    except NoSuchElementException:
        return 0
    
    
    total_pattern = r"(?:(?<=Ad \d of )|(?<=Sponsored \d of ))\d"
    current_pattern = r"(?:(?<=Ad )|(?<=Sponsored ))\d"

    total_match = re.search(total_pattern, ad_text)
    current_match = re.search(current_pattern, ad_text)

    if total_match and current_match:
        return int(total_match[0]) - int(current_match[0])
    
    return 0


def get_ad_order(driver) -> int:

    try:
        ad_text = driver.find_element(By.CSS_SELECTOR, ".ytp-ad-simple-ad-badge > .ytp-ad-text").get_attribute("innerHTML")
    except NoSuchElementException:
        return 0

    pattern = r"(?:(?<=Ad )|(?<=Sponsored ))\d"
    match = re.search(pattern, ad_text)
    if match:
        return int(match[0])
    
    if "Ad" or "Sponsored" in ad_text:
        return 1
    
    return 0

def get_reasons(driver) -> list:
    try:
        WebDriverWait(driver, 3).until(EC.presence_of_element_located(
            (By.CLASS_NAME, "QVfAMd-wPzPJb-xPjCTc-ibnC6b")
        ))
        google_info = driver.find_elements(By.CLASS_NAME, "QVfAMd-wPzPJb-xPjCTc-ibnC6b")
        google_info = [element.get_attribute('textContent') for element in google_info]
    except:
        google_info = []
    try:
        WebDriverWait(driver, 3).until(EC.presence_of_element_located(
            (By.CLASS_NAME, "zpMl8e-C2o4Ve-wPzPJb-xPjCTc-ibnC6b")
        ))
        other_info = driver.find_elements(By.CLASS_NAME, "zpMl8e-C2o4Ve-wPzPJb-xPjCTc-ibnC6b")
        other_info = [element.get_attribute('innerHTML') for element in other_info] 
    except:
        other_info = []
    
    if not google_info + other_info:
        current_stamp = get_test_id()
        username = get_username(driver)
        try:
            driver.save_screenshot(f"error_screenshots_{username}/no_targeting_reasons_{current_stamp}.png")
        except:
            pass

    return google_info + other_info


def get_iframe_routine(driver, username, video_id, type_of_ad, wait_time) -> tuple:
    # type_of_ad = "side", "preroll", "preroll_companion", "promoted_video"

    reasons, advertiser_info = None, None

    try:
        WebDriverWait(driver, wait_time).until(EC.presence_of_element_located(
            (By.ID, "iframe")
        ))
        iframe = driver.find_element(By.ID, "iframe")
        
    except:

        current_stamp = get_test_id()

        print(f"{username}: detected {type_of_ad} ad but no iframe, video_id: {video_id}")
        driver.save_screenshot(f"error_screenshots_{username}/{type_of_ad}_no_iframe_{video_id}_{current_stamp}.png")

        switch_back(driver)

        if type_of_ad == "preroll":
            return get_preroll_ad_companion_info(driver)

        return None, None

    try:
        driver.switch_to.frame(iframe)
        WebDriverWait(driver, wait_time).until(EC.presence_of_element_located(
            (By.XPATH, '//div[text()="My Ad Center"]')
        ))

        reasons = get_reasons(driver)
        advertiser_info = get_advertiser_info(driver)

    except:
        try:
            # try re-clicking the iframe one more time
            switch_back(driver)
            iframe = driver.find_element(By.ID, "iframe")
            driver.switch_to.frame(iframe)

            reasons = get_reasons(driver)
            advertiser_info = get_advertiser_info(driver)
            return reasons, advertiser_info
        except:
            pass

        current_stamp = get_test_id()
        
        print(f"{username}: {type_of_ad} ad iframe timed out, video_id: {video_id}")
        driver.save_screenshot(f"error_screenshots_{username}/{type_of_ad}_timedout_{video_id}_{current_stamp}.png")
        switch_back(driver)
        return reasons, advertiser_info

    try:
        exit_info_iframe(driver)
    except:
        current_stamp = get_test_id()
        
        print(f"{username}: can't exit from {type_of_ad} ad popup, video_id: {video_id}")
        driver.save_screenshot(f"error_screenshots_{username}/{type_of_ad}_timedout_{current_stamp}.png")

        raise IframeExitException()

    return reasons, advertiser_info


def exit_info_iframe(driver):

    try:
        exit_button = driver.find_element(
            By.CSS_SELECTOR, ".VfPpkd-Bz112c-LgbsSe.yHy1rc.eT1oJ.mN1ivc.zBmRhe-LgbsSe" 
        )
        driver.execute_script("arguments[0].click();", exit_button)
    except:
        pass
    
    switch_back(driver)


def get_advertiser_info(driver) -> tuple:

    advertiser_name, advertiser_loc = None, None

    try:
        ad_container = driver.find_elements(By.CLASS_NAME, "G5HdJb-fmcmS")
        if ad_container:
            advertiser_name = ad_container[0].get_attribute("innerHTML")
            advertiser_loc = ad_container[1].get_attribute("innerHTML")
    except IndexError:
        return advertiser_name, None
    except NoSuchElementException:
        pass

    return advertiser_name, advertiser_loc


def get_preroll_ad_companion_info(driver) -> tuple:

    username = get_username(driver)
    video_id = get_video_id(driver.current_url)

    try:
        info_button = driver.find_element(By.CSS_SELECTOR, "#action-companion-ad-info-button").find_element(By.CSS_SELECTOR, "button")
        driver.execute_script("arguments[0].click();", info_button)

    except NoSuchElementException:
        
        print(f"{username}: preroll ad companion info button is not found")
        driver.save_screenshot(f"error_screenshots_{username}/no_preroll_ad_companion_info_button_{video_id}.png") 

        return None, None
    
    return get_iframe_routine(driver, username, video_id, "preroll_companion", 2)

def get_preroll_ad_info(driver) -> tuple:

    username = get_username(driver)
    video_id = get_video_id(driver.current_url)
    reasons, advertiser_info = None, None

    try:
        WebDriverWait(driver, 2).until(EC.presence_of_element_located(
            (By.CSS_SELECTOR,
            "button.ytp-ad-button.ytp-ad-button-link.ytp-ad-clickable")
        ))
        info_button = driver.find_element(
            By.CSS_SELECTOR,
            "button.ytp-ad-button.ytp-ad-button-link.ytp-ad-clickable"
        )
        time.sleep(1)
        driver.execute_script("arguments[0].click();", info_button)
        
    except:
        
        msg = f"{username}: preroll ad info button is not found"
        print(msg)
        video_id = get_video_id(driver.current_url)
        driver.save_screenshot(f"error_screenshots_{username}/no_preroll_ad_info_button_{video_id}.png") 
        return get_preroll_ad_companion_info(driver)


    try:
        reason_container = driver.find_element(By.CSS_SELECTOR, ".ytp-ad-info-dialog-ad-reasons")
        li = reason_container.find_elements(By.CSS_SELECTOR,"li")
        reasons = [element.get_attribute('innerHTML') for element in li] 
        return reasons, get_advertiser_info(driver)
    except NoSuchElementException:
        pass

    return get_iframe_routine(driver, username, video_id, "preroll", 2)


def get_preroll_ad_id(driver) -> str | None:

    try:
        # right clicking the video and opening the "stats for nerds" menu
        action = ActionChains(driver)
        video_player = driver.find_element(
            By.CSS_SELECTOR, "#movie_player > div.html5-video-container > video"
        )
        action.context_click(video_player).perform()
        stats_button = driver.find_element(
            By.CSS_SELECTOR,
            "div.ytp-popup.ytp-contextmenu > div > div > div:nth-child(7)",
        )
        driver.execute_script("arguments[0].click();", stats_button)
        id_element = driver.find_element(By.CSS_SELECTOR, ".ytp-sfn-cpn")

        # use split to extract only the video id characters
        ad_id = id_element.text.split()[0]

        exit_button = driver.find_element(
            By.CSS_SELECTOR, "button.html5-video-info-panel-close.ytp-button"
        )
        driver.execute_script("arguments[0].click();", exit_button)
        return ad_id

    except NoSuchElementException:
        return None
    except ElementNotInteractableException:
        return None
    except IndexError:
        print(f"index error, returning id_element.text = {id_element.text}")
        return id_element.text

    
def get_preroll_ad_companion_site(driver) -> tuple:

    try:
        site = driver.find_element(By.CSS_SELECTOR, "span#domain").get_attribute("innerHTML").strip()
    except NoSuchElementException:
        return None, None
    
    try:
        header = driver.find_element(By.CSS_SELECTOR,".style-scope.ytd-action-companion-ad-renderer#header").get_attribute("innerHTML").strip()
    except NoSuchElementException:
        return site, None
    
    return site, header

def get_preroll_ad_site(driver) -> tuple:

    site, card_headline, card_descr = "", "", ""

    # site is usually the link to advertiser's site, but sometimes it's just the site name
    try:
        site = driver.find_element(
            By.CSS_SELECTOR,
            "button.ytp-ad-button.ytp-ad-visit-advertiser-button.ytp-ad-button-link"
        ).get_attribute("aria-label").strip()

    except NoSuchElementException:
        pass
    
    try:
        card_headline = driver.find_element(By.CSS_SELECTOR, ".ytp-ad-text.ytp-flyout-cta-headline").get_attribute("innerHTML").strip()
    except NoSuchElementException:
        pass

    try:
        card_descr = driver.find_element(By.CSS_SELECTOR, ".ytp-ad-text.ytp-flyout-cta-description").get_attribute("innerHTML").strip()
    except NoSuchElementException:
        pass

    card = card_headline + " " + card_descr
    card = card if card.strip() else None

    if not site:
        return get_preroll_ad_companion_site(driver)

    return site, card
    



def get_side_ad_info(driver) -> tuple:

    username = get_username(driver)
    video_id = get_video_id(driver.current_url)

    try:
        menu_button = driver.find_element(
            By.CSS_SELECTOR,
            ".style-scope.ytd-promoted-sparkles-web-renderer > yt-icon-button > button",
        )
        time.sleep(1)
        driver.execute_script("arguments[0].click();", menu_button)

    except NoSuchElementException:
        return None, None

    
    # potentially deprecated drop-down menu that has My Ad Center as an option
    try:

        info_button = driver.find_element(
            By.CSS_SELECTOR,
            "#items > ytd-menu-navigation-item-renderer.style-scope.ytd-menu-popup-renderer.iron-selected > a > tp-yt-paper-item",
        )

        driver.execute_script("arguments[0].click();", info_button)
    except NoSuchElementException:
        pass
    except:
        print(f"{username}: can't click side info button")
        print(traceback.format_exc())
        pass
        
    return get_iframe_routine(driver, username, video_id, "side", 5)


def get_side_ad_site(driver):

    # site is usually the link to advertiser's site, but sometimes it's just the site name

    try:
        side_ad_container = driver.find_element(By.CSS_SELECTOR, "#website-text")
        site = side_ad_container.get_attribute("innerHTML").strip()
        return site
    except NoSuchElementException:
        return None



def click_side_ad(driver):

    try:

        element = driver.find_element(
            By.CSS_SELECTOR,
            ".style-scope.ytd-promoted-sparkles-web-renderer > yt-button-shape > button"
        )

        driver.execute_script("arguments[0].click();", element)
    except NoSuchElementException:
        return None

    # save current tab and switch chromedriver's focus to the new tab
    video_tab = driver.current_window_handle
    tabs_open = driver.window_handles
    driver.switch_to.window(tabs_open[1])
    
    url = driver.current_url
    while url == "about:blank":
        url = driver.current_url
    driver.execute_script("window.stop();")
    url = driver.current_url
    driver.close()
    driver.switch_to.window(video_tab)
    return url

def click_preroll_ad(driver):

    try:
        element = driver.find_element(
            By.CSS_SELECTOR,
            "button.ytp-ad-button.ytp-ad-visit-advertiser-button.ytp-ad-button-link"
        )

        driver.execute_script("arguments[0].click();", element)
    except NoSuchElementException:
        return None

    # save current tab and switch chromedriver's focus to the new tab
    video_tab = driver.current_window_handle
    tabs_open = driver.window_handles
    driver.switch_to.window(tabs_open[1])
    
    url = driver.current_url
    while url == "about:blank":
        url = driver.current_url
    driver.execute_script("window.stop();")
    url = driver.current_url
    driver.close()
    driver.switch_to.window(video_tab)
    return url

def get_side_ad_text(driver):

    title, body = "", ""

    try:
        title_container = driver.find_element(By.CSS_SELECTOR, "#title.style-scope.ytd-promoted-sparkles-web-renderer.yt-simple-endpoint")
        title = title_container.get_attribute("innerHTML").strip()
    except NoSuchElementException:
        pass

    try:
        body_container = driver.find_element(By.CSS_SELECTOR, "#description.style-scope.ytd-promoted-sparkles-web-renderer.yt-simple-endpoint")
        body = body_container.get_attribute("innerHTML").strip()
    except NoSuchElementException:
        pass

    text = title + body
    text = text if text else None
    return text


def get_side_ad_img(driver):

    try:
        img_container = driver.find_element(By.CSS_SELECTOR, "#thumbnail.style-scope.ytd-promoted-sparkles-web-renderer > img")
        img_src = img_container.get_attribute("src")
    except NoSuchElementException:
        return None

    return img_src


def get_promoted_video_title(driver):


    try:
        container = driver.find_element(By.CSS_SELECTOR, "#video-title.style-scope.ytd-compact-promoted-video-renderer")
        title = container.get_attribute("title")
    except NoSuchElementException:
        return None

    return title


def get_promoted_video_channel(driver) -> str:

    try:
        ad_container = driver.find_element(By.CSS_SELECTOR, "#endpoint-link.yt-simple-endpoint.style-scope.ytd-compact-promoted-video-renderer")
        channel_container = ad_container.find_element(By.CSS_SELECTOR, "#text > a")
        channel = channel_container.get_attribute("innerHTML")
        return channel
    except NoSuchElementException:
        return None



def get_promoted_video_info(driver) -> tuple:

    username = get_username(driver)
    video_id = get_video_id(driver.current_url)

    try:
        menu_button = driver.find_element(
            By.CSS_SELECTOR,
            ".style-scope.ytd-compact-promoted-video-renderer > yt-icon-button > button")
        time.sleep(1)
        driver.execute_script("arguments[0].click();", menu_button)
    except NoSuchElementException:
        return None, None
    
    try:
        WebDriverWait(driver, 1).until(EC.presence_of_element_located(
            (By.CSS_SELECTOR,
            "#items > ytd-menu-navigation-item-renderer > a > tp-yt-paper-item",
            )
        ))
        info_button = driver.find_element(
            By.CSS_SELECTOR,
            "#items > ytd-menu-navigation-item-renderer > a > tp-yt-paper-item"
        )
        time.sleep(1)
        driver.execute_script("arguments[0].click();", info_button)
    except:
        pass

    return get_iframe_routine(driver, username, video_id, "promoted_video", 2)


def get_promoted_video_url(driver) -> str | None:

    try:
        element = driver.find_element(
            By.CSS_SELECTOR,
            "#rendering-content > ytd-compact-promoted-video-renderer > div > a",
        )

        raw_url = element.get_attribute("href")
        pattern = r"(?<=video_id=).{11}"
        match = re.search(pattern, raw_url)

        if match:
            return "https://www.youtube.com/watch?v=" + match[0]

    except NoSuchElementException:
        return None



