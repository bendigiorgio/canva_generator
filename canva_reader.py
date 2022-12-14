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
import tkinter as tk

img_path = "/Users/bdigio17/Documents/Python_git/Python_ML/nikko_name/menu.jpg"
load_dotenv()
breakfast_link = os.environ.get("BF_LINK")
lunch_link = os.ebviron.get("LUNCH_LINK")



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
    month = int(month.rpartition("月", False)[0])

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

    # Remove unused lines
    text_df["Text"] = text_df["Text"].str.rpartition("・", False)[
        2
    ]  # Remove all to the left of ・
    text_df.drop(text_df.loc[text_df["Text"].str.len() <= 1].index, inplace=True)
    text_df.dropna()
    text_df.drop(text_df["Text"].str.contains(buffet_type), inplace=True)
    text_df.drop(text_df[text_df["Text"].str.contains("プレミアム")].index, inplace=True)

    return month, is_premium, buffet_type, text_df


# Creates the canva document
def to_canva(df: pd.DataFrame, month: int, is_premium: bool, buffet_type: str) -> str:
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
    driver.switch_to.window(driver.window_handles[-1])  # last opened tab handle
    driver.find_element(By.XPATH, '//input[@aria-label="Design title"]').send_keys(
        f"{month}_{buffet_type}"
    )

    # Creates pages for every item
    for i in range(len(df)):
        driver.find_element(
            By.XPATH, '//div[@class="_8VoL_g"]/button[@aria-label="Duplicate page"]'
        ).click()
        time.sleep(0.5)
        driver.find_element_by_xpath("//body").send_keys(Keys.HOME)

    # Add text to each card
    for line in df["Text"].iterrows():
        driver.find_element(
            By.XPATH, '//div[@class="_3stTEQ imh8lg z8nqQQ"]/p[text()="."]'
        ).click()
        driver.find_element(
            By.XPATH, '//div[@class="_3stTEQ imh8lg z8nqQQ"]/p[text()="."]'
        ).click()
        driver.find_element(
            By.XPATH, '//div[@class="_3stTEQ imh8lg z8nqQQ"]/p[text()="."]'
        ).send_keys(line)
        time.sleep(0.5)
        driver.find_element_by_xpath('//div[@class="efGBqA"]').click()
        driver.find_element_by_xpath("//body").send_keys(Keys.PAGE_DOWN)

    # Gets shareable link
    driver.find_element(By.XPATH, '//button[@aria-describedby="__a11yId80').click()
    driver.find_element(By.XPATH, '//button[@aria-describedby="__a11yId85').click()
    driver.find_element(By.XPATH, '//li[@id="__a11yId83--2"]/button').click()
    driver.find_element(By.XPATH, '//button[@aria-label="Copy link"').click()

    # Gets link from clipboard
    root = tk.Tk()
    canva_link = root.clipboard_get()
    root.destroy()  # Destroy the Tkinter instance
    driver.quit() # Destroy the Selenium Browser Instance

    return canva_link