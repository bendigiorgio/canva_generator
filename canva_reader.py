import os
import time
from paddleocr import PaddleOCR
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

load_dotenv()
breakfast_link = os.environ.get("BF_LINK")
lunch_link = os.ebviron.get("LUNCH_LINK")



img_path = "/Users/bdigio17/Documents/Python_git/Python_ML/nikko_name/menu.jpg"


def get_text(image_path: str) -> pd.DataFrame:
    ocr = PaddleOCR(use_angle_cls=True, lang="japan")
    df_columns = ["Text", "Score"]
    result = ocr.ocr(img_path, cls=True)

    # Take only to score and text from the result
    cur_text = list(result[0][1][1])

    # Convert results into dataframe
    df = pd.DataFrame(columns=df_columns)

    for i in range(len(result[0])):
        cur_text = list(result[0][i][1])
        cur_text = pd.DataFrame([cur_text], columns=df_columns)
        # pd.concat([df,cur_text], ignore_index=True)
        df = df.append(cur_text)

    return df


def clean_text(text_df: pd.DataFrame) -> tuple[int, bool, str, pd.DataFrame]:
    month = text_df[text_df["Text"].str.contains("月")]
    if len(month) > 3 or None:
        raise ValueError("No Month Detected in the Text")

    # Take only the number value for month
    month = int(month.rpartition("月")[0])

    # Check if it is a premium buffet
    premium = text_df[text_df["Text"].str.contains("プレミアム")]
    if premium != "":
        is_premium = True

    # Check the type of buffet
    if text_df["Text"].str.contains("朝食").any():
        buffet_type = "朝食"
    elif text_df["Text"].str.contains("ランチ").any():
        buffet_type = "ランチ"
    elif text_df["Text"].str.contains("ディナー").any():
        buffet_type = "ディナー"

    # Mark low score text
    text_df["Acc_Warning"] = text_df["Score"].apply(lambda x: 0 if x >= 0.8 else 1)

    return month, is_premium, buffet_type, text_df


def to_canva(df: pd.DataFrame, month:int, is_premium: bool, buffet_type: str) -> str:
    driver = webdriver.Chrome("/usr/local/bin/chromedriver")
    wait = WebDriverWait(driver, 10)
    if buffet_type == "朝食":
        driver.get(breakfast_link)
    elif buffet_type == "ランチ" or "ディナー":
        driver.get(lunch_link)
    time.sleep(1)
    driver.find_element(By.XPATH, '//button/span[text()="File"]').click()
    driver.find_element(By.XPATH, '//button/span[text()="Make a copy"]').click()
    wait.until(EC.number_of_windows_to_be(2))
    driver.switch_to.window(driver.window_handles[-1]) # last opened tab handle
    driver.find_element(By.XPATH, '//input[@aria-label="Design title"]').send_keys(f'{month}_{buffet_type}')
    driver.find_element(By.XPATH, '//div[@class="_3stTEQ imh8lg z8nqQQ"]/p[text()="."]').click() 
    driver.find_element(By.XPATH, '//div[@class="_3stTEQ imh8lg z8nqQQ"]/p[text()="."]').click()
    driver.find_element(By.XPATH, '//div[@class="_3stTEQ imh8lg z8nqQQ"]/p[text()="."]').send_keys() 
    return canva_link
