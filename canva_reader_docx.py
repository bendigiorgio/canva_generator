import os
import io
import time
from docx import Document
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pyperclip
import keyboard
import tkinter as tk
import re

doc_path = "/Users/bdigio17/Documents/Python_git/Python_ML/nikko_name/12menu.docx"
load_dotenv()
breakfast_link = os.environ.get("BF_LINK")
lunch_link = os.environ.get("LUNCH_LINK")



def get_text(doc_path: str) -> pd.DataFrame:
    document = '\n'.join([p.text for p in Document(doc_path).paragraphs])
    df = pd.read_csv(io.StringIO(document))
    return df

def clean_text(df):
    # Take only the number value for month
    month = int(re.findall('\d+', df["Text"][1])[0])
    if df["Text"].str.contains("朝食").any():
            buffet_type = "朝食"

    elif df["Text"].str.contains("ランチ").any():
        buffet_type = "ランチ"

    elif df["Text"].str.contains("ディナー").any():
        buffet_type = "ディナー"

    df.drop([0,1], inplace=True)
    # df["Text"] = df["Text"].str.rpartition("・", False)[2]  # Remove all to the left of ・
    split = df["Text"].str.split("・",expand=True)
    df["Text"] = split[1]
    df.dropna(inplace=True)
    return df, month, buffet_type

# Creates the canva document
def to_canva(df: pd.DataFrame, month: int, is_premium: bool, buffet_type: str) -> str:
    driver = webdriver.Chrome("/usr/local/bin/chromedriver")
    wait = WebDriverWait(driver, 10)
    if buffet_type == "朝食":
        driver.get(breakfast_link)
    elif buffet_type == "ランチ" or "ディナー":
        driver.get(lunch_link)
    time.sleep(1)
    driver.find_element(By.XPATH, '//button/span[text()="Edit design"]').click()
    driver.find_element(By.XPATH, '//button/span[text()="Accept all cookies"]').click()
    driver.find_element(By.XPATH, '//button/span[text()="Continue with Google"]').click()
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

def to_clipboard(text):
    pyperclip.copy(text)

def copy_all(df):
    text_list = df["Text"].to_list() 
    cur_index = 0
    pyperclip.copy(text_list[cur_index])
    print(text_list[cur_index])
    while cur_index <= len(text_list)-1:
        if keyboard.is_pressed('windows+v'):
            pyperclip.copy(text_list[cur_index])
            cur_index += 1
            print(text_list[cur_index])
            time.sleep(1)
    print("All lines copied and pasted")

test = get_text(doc_path)
df, text_month, buffet = clean_text(test)

# to_canva(df, text_month, False, buffet)
copy_all(df)