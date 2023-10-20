from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import *
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from google.cloud import storage

import json
import time
import datetime
import glob
import os
import traceback
import re


def upload_blob(project_name, bucket_name, source_file_name, destination_blob_name):
    # upload to gcp

    storage_client = storage.Client(project=project_name)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)


def upload_from_directory(project_name, bucket_name, source_dir, destination_dir):
    # dir_name = "dir/"

    rel_paths = glob.glob(source_dir + '**', recursive=True)
    storage_client = storage.Client(project=project_name)
    bucket = storage_client.bucket(bucket_name)
    for local_file in rel_paths:
        remote_path = f'{destination_dir}{"/".join(local_file.split(os.sep)[1:])}'
        if os.path.isfile(local_file):
            blob = bucket.blob(remote_path)
            blob.upload_from_filename(local_file)


def create_driver(config_path="", headless=True, page_load_strategy="normal"):
    # config is a json file
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1540,1080")
    # options.add_argument("--no-sandbox") # only for linux vm
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-extensions")
    
    if headless:
        options.add_argument("--headless=new")


    config = {}
    if config_path:
        config_f = open(config_path, 'r')
        config = json.load(config_f)
        config_f.close()
        if config['user_data']:
            options.add_argument("user-data-dir=" + config['user_data'])

    # "eager" strategy is when DOM access is available but full page isn't necessarily loaded
    # https://www.selenium.dev/documentation/webdriver/drivers/options/

    caps = DesiredCapabilities.CHROME
    caps["pageLoadStrategy"] = page_load_strategy
        
    driver = webdriver.Chrome(options=options, desired_capabilities=caps)

    try:
        login(driver, "https://accounts.google.com/signin/v2/identifier?service=youtube", config['username'], config['password'])
        login(driver, "https://www.gmail.com", config['username'], config['password'])
    except:
        pass

    check_login(driver, config["username"])

    return driver


def login(driver, url, username, password):

    driver.get(url)
    time.sleep(2)

    uEntry = driver.find_element("id","identifierId")
    uEntry.clear()
    uEntry.send_keys(username)
    
    div = driver.find_element(By.ID, "identifierNext")
    driver.execute_script("arguments[0].click();", div)

    WebDriverWait(driver, 4).until(EC.presence_of_element_located((By.ID, 'password')))
    pEntry = driver.find_element(By.ID, "password")
    pEntry = pEntry.find_element(By.XPATH, './/input[@type="password"]')
    pEntry.clear()
    pEntry.send_keys(password)
    time.sleep(1)
    pEntry.send_keys(Keys.RETURN)
    time.sleep(2)



def check_login(driver, username):

    driver.get("https://www.gmail.com")
    time.sleep(2)
    if username in driver.title:
        return
    else:
        print(f"{username}: login not successful")
        # Assuming headless is False, can do verification step here
        time.sleep(30)
    
    driver.get("https://www.gmail.com")

    try:
        assert(username in driver.title)
    except AssertionError:
        current_stamp = get_test_id()
        driver.save_screenshot(f"error_screenshots_{username}/login_issues_{current_stamp}.png")
        raise AssertionError(f"{username}: login failed")

def get_test_id():
    # Generates an id for scraping run based on system time
    d = datetime.datetime.now()
    test_str = '{date:%m%d_%H%M}'.format(date = d)

    return test_str


def switch_back(driver):
    driver.switch_to.default_content()

def get_video_id(url):

    pattern = r"(?<=watch\?v=).{11}" #capture anything with 11-length after watch?v=
    match = re.search(pattern, url)

    if match:
        return match[0]
    return None


def get_username(driver):

    data_dir = driver.__getattribute__("caps")["chrome"]["userDataDir"]
    pattern = r"(?<=UserData_)\S*"
    match = re.search(pattern, data_dir)

    if match:
        return match[0]
    
    return None


def collect_interests(driver):

    time.sleep(1)
    
    try:
        driver.get("https://myadcenter.google.com/customize")
        interest_cards = driver.find_elements(By.CLASS_NAME, "YcxLyd")
        interests = [i.get_attribute("innerHTML") for i in interest_cards]

        return interests
    except (IndexError, NoSuchElementException) as e:
        return None


def collect_brands(driver):

    time.sleep(1)

    try:
        driver.get("https://myadcenter.google.com/customize")
        brand_button = driver.find_elements(By.CSS_SELECTOR, ".VfPpkd-AznF2e.WbUJNb.FEsNhd")[1]
        tab_name = brand_button.find_element(By.CSS_SELECTOR, ".VfPpkd-jY41G-V67aGc").get_attribute("innerHTML")

        if tab_name == "Brands":
            driver.execute_script("arguments[0].click();", brand_button)
            time.sleep(1)
            brand_list = driver.find_elements(By.CLASS_NAME, "ByHevf")
            brands = [i.get_attribute("innerHTML") for i in brand_list]
        else:
            return None

        return brands
    except (IndexError, NoSuchElementException) as e:
        return None 
    

def turn_on_ad_personalization(driver):

    username = get_username(driver)
    time.sleep(2)

    ad_center_url = "https://myadcenter.google.com/"
    driver.get(ad_center_url)

    try:
        toggle_button = driver.find_element(By.CSS_SELECTOR, ".ie6Hvb-eIzVJe-LgbsSe.nOY0Nb.sly7Kb.DmnIhf")
        driver.execute_script("arguments[0].click();", toggle_button)
    except NoSuchElementException:
        driver.find_element(By.CSS_SELECTOR, ".ie6Hvb-eIzVJe-LgbsSe.nOY0Nb.sly7Kb.YFjIb")
        print(f"{username}: Ad personalization is already on")
        return
    
    time.sleep(1)

    turn_on_button = driver.find_element(By.CSS_SELECTOR, "button.mUIrbf-LgbsSe.mUIrbf-LgbsSe-OWXEXe-dgl2Hf[data-mdc-dialog-action='ok']")
    driver.execute_script("arguments[0].click();", turn_on_button)
    
    time.sleep(1)
    try:
        got_it_button = driver.find_element("xpath", '//span[text()="Got it"]')
        got_it_button.click()
    except NoSuchElementException:
        pass

    print(f"{username}: Ad personalization is turned on")
    

def turn_off_ad_personalization(driver):

    username = get_username(driver)
    time.sleep(2)

    ad_center_url = "https://myadcenter.google.com/"
    driver.get(ad_center_url)

    try:
        toggle_button = driver.find_element(By.CSS_SELECTOR, ".ie6Hvb-eIzVJe-LgbsSe.nOY0Nb.sly7Kb.YFjIb")
        driver.execute_script("arguments[0].click();", toggle_button)
    except NoSuchElementException:
        driver.find_element(By.CSS_SELECTOR, ".ie6Hvb-eIzVJe-LgbsSe.nOY0Nb.sly7Kb.DmnIhf")
        print(f"{username}: Ad personalization is already off")
        return
    
    time.sleep(1)

    turn_off_button = driver.find_element(By.CSS_SELECTOR, "button.mUIrbf-LgbsSe.mUIrbf-LgbsSe-OWXEXe-dgl2Hf[data-mdc-dialog-action='ok']")
    driver.execute_script("arguments[0].click();", turn_off_button)
    
    time.sleep(1)
    try:
        got_it_button = driver.find_element("xpath", '//span[text()="Got it"]')
        got_it_button.click()
    except NoSuchElementException:
        pass
    
    print(f"{username}: Ad personalization is turned off")
    
    

def turn_on_activity(driver):

    username = get_username(driver)
    time.sleep(2)
    
    activity_controls_url = "https://myactivity.google.com/activitycontrols?settings=search"
    driver.get(activity_controls_url)

    try:
        turn_on_button = driver.find_element("xpath", '//span[text()="Turn on"]')
        driver.execute_script("arguments[0].click();", turn_on_button)
    except NoSuchElementException:
        driver.find_element("xpath", '//span[text()="Turn off"]')
        print(f"{username}: Activity is already on")
        return
    
    time.sleep(1)
    # Scroll to bottom of popup to enable Turn on activity
    popup = driver.find_element(By.CSS_SELECTOR, ".cSvfje")
    driver.execute_script("arguments[0].scroll(0, arguments[0].scrollHeight);", popup)

    time.sleep(1)

    final_button = driver.find_element(
        By.CSS_SELECTOR,
        "button.VfPpkd-LgbsSe.VfPpkd-LgbsSe-OWXEXe-k8QpJ.VfPpkd-LgbsSe-OWXEXe-dgl2Hf.nCP5yc.AjY5Oe.DuMIQc.LQeN7.QWgF9b",
    )
    driver.execute_script("arguments[0].click();", final_button)

    time.sleep(1)
    try:
        got_it_button = driver.find_element("xpath", '//span[text()="Got it"]')
        got_it_button.click()
    except NoSuchElementException:
        pass

    print(f"{username}: Activity is turned on")



def turn_off_activity(driver):

    username = get_username(driver)
    time.sleep(2)

    activity_controls_url = "https://myactivity.google.com/activitycontrols?settings=search"
    driver.get(activity_controls_url)

    try:
        turn_off_button = driver.find_element("xpath", '//span[text()="Turn off"]')
        driver.execute_script("arguments[0].click();", turn_off_button)
    except NoSuchElementException:
        driver.find_element("xpath", '//span[text()="Turn on"]')
        print(f"{username}: Activity is already off")
        return

    time.sleep(2)
    final_button = driver.find_element(
        By.CSS_SELECTOR, "li.DMSrld.VfPpkd-StrnGf-rymPhb-ibnC6b"
    )
    driver.execute_script("arguments[0].click();", final_button)

    time.sleep(1)
    try:
        got_it_button = driver.find_element("xpath", '//span[text()="Got it"]')
        got_it_button.click()
    except NoSuchElementException:
        pass

    print(f"{username}: Activity is turned off")



def turn_off_youtube_history(driver):

    username = get_username(driver)
    time.sleep(2)

    history_controls_url = "https://myactivity.google.com/product/youtube/controls"
    driver.get(history_controls_url)

    try:
        turn_off_button = driver.find_element("xpath", '//span[text()="Turn off"]')
        turn_off_button.click()
    except NoSuchElementException:
        driver.find_element("xpath", '//span[text()="Turn on"]')
        print(f"{username}: YouTube history is already off")
        return
    
    time.sleep(1)
    pause_button = driver.find_element(
        By.CSS_SELECTOR, "button.VfPpkd-LgbsSe.VfPpkd-LgbsSe-OWXEXe-k8QpJ.VfPpkd-LgbsSe-OWXEXe-dgl2Hf.nCP5yc.AjY5Oe.DuMIQc.LQeN7.yARu6e"
    ) 
    driver.execute_script("arguments[0].click();", pause_button)

    time.sleep(1)
    try:
        got_it_button = driver.find_element("xpath", '//span[text()="Got it"]')
        got_it_button.click()
    except NoSuchElementException:
        pass

    print(f"{username}: YouTube history is turned off")


def turn_on_youtube_history(driver):

    username = get_username(driver)
    time.sleep(2)

    history_controls_url = "https://myactivity.google.com/product/youtube/controls"
    driver.get(history_controls_url)
    
    try:
        turn_on_button = driver.find_element("xpath", '//span[text()="Turn on"]')
        turn_on_button.click()
    except NoSuchElementException:
        driver.find_element("xpath", '//span[text()="Turn off"]')
        print(f"{username}: YouTube history is already on")
        return

    time.sleep(1)
    try:
        final_button = driver.find_element(
            By.CSS_SELECTOR,
            "button.VfPpkd-LgbsSe.VfPpkd-LgbsSe-OWXEXe-k8QpJ.VfPpkd-LgbsSe-OWXEXe-dgl2Hf.nCP5yc.AjY5Oe.DuMIQc.LQeN7.yARu6e",
        )
        final_button.click()
    except NoSuchElementException:
        pass

    time.sleep(1)
    try:
        got_it_button = driver.find_element("xpath", '//span[text()="Got it"]')
        got_it_button.click()
    except NoSuchElementException:
        pass

    print(f"{username}: YouTube history is turned on")


def turn_off_location(driver):

    username = get_username(driver)
    time.sleep(2)

    location_url = "https://myadcenter.google.com/controls/ads-data/historical-location"
    driver.get(location_url)

    try:
        toggle_button = driver.find_element(By.CSS_SELECTOR, ".nhf33 > button")
        current_status = toggle_button.get_attribute("aria-checked")
    except NoSuchElementException:
        time.sleep(1)

        # if ad personaliztion is off, will be redirected
        current_url = driver.current_url
        if current_url == "https://myadcenter.google.com/personalizationoff":
            print(f"{username}: Location is already off, redirected")
            return
        

    if current_status == "true":
        driver.execute_script("arguments[0].click();", toggle_button)
        time.sleep(2)
        turn_off_button = driver.find_element("xpath", '//span[text()="Turn off"]')
        driver.execute_script("arguments[0].click();", turn_off_button)
        print(f"{username}: Location used for ads is turned off")
    else:
        print(f"{username}: Location is already off")
    


def delete_activity(driver):

    username = get_username(driver)
    time.sleep(3)

    activity_history_url = "https://myactivity.google.com/myactivity"
    driver.get(activity_history_url)

    delete_button = driver.find_element("xpath", '//span[text()="Delete"]')
    driver.execute_script("arguments[0].click();", delete_button)

    time.sleep(1)

    all_time_button = driver.find_element(
        By.CSS_SELECTOR, "div.cSvfje > ul > li:nth-child(3)"
    )
    driver.execute_script("arguments[0].click();", all_time_button)

    time.sleep(2)

    try:
        next_button = driver.find_element("xpath", '//span[text()="Next"]')
        driver.execute_script("arguments[0].click();", next_button)
    except NoSuchElementException:
        pass

    time.sleep(1)

    delete_button = driver.find_element("xpath", '//span[text()="Delete"]')
    driver.execute_script("arguments[0].click();", delete_button)

    try:
        final_delete_button = driver.find_element(
            By.CSS_SELECTOR,
            "button.VfPpkd-LgbsSe.VfPpkd-LgbsSe-OWXEXe-k8QpJ.nCP5yc.AjY5Oe.DuMIQc.LQeN7.e6p9Rc",
        )
        final_delete_button.click()
    except NoSuchElementException:
        try:
            no_activity_text = driver.find_element(By.CLASS_NAME, "oDnphc").get_attribute("innerHTML")
            if "You have no selected activity" in no_activity_text:
                print(f"{username}: No activity to delete")
                return
        except NoSuchElementException:
            print(f"{username}: unexpected")
            print(traceback.format_exc())
            time.sleep(2)
            raise AssertionError("can't delete activity")
        
    time.sleep(1)
    try:
        got_it_button = driver.find_element("xpath", '//span[text()="Got it"]')
        got_it_button.click()
    except NoSuchElementException:
        pass

    print(f"{username}: Activity is deleted")


def change_gender(driver, target_gender):
    # target_gender: "female", "male", "rather not say" corresponding to 3 options in Google profile

    username = get_username(driver)

    time.sleep(1)
    gender_change_url = "https://myaccount.google.com/gender?continue=https%3A%2F%2Fmyaccount.google.com%2Fprofile"
    driver.get(gender_change_url)

    id_dict = {}
    text_labels = driver.find_elements(By.CSS_SELECTOR, f".VfPpkd-V67aGc")
    for label in text_labels:
        gender_id = label.get_attribute("for")
        gender_label = label.text.strip().lower()
        id_dict[gender_label] = gender_id

    target_gender = target_gender.lower()
    id_value = id_dict[target_gender]

    radio_button = driver.find_element(By.CSS_SELECTOR, f".VfPpkd-gBXA9-bMcfAe[id='{id_value}']")
    driver.execute_script("arguments[0].click();", radio_button)

    print(f"{username}: Changed gender to {target_gender}")




