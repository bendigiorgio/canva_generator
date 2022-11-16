from paddleocr import PaddleOCR
import numpy as np
import pandas as pd


img_path = '/Users/bdigio17/Documents/Python_git/Python_ML/nikko_name/menu.jpg'


def get_text(image_path: str) -> pd.DataFrame:
    ocr = PaddleOCR(use_angle_cls=True, lang='japan')
    df_columns = ['Text', 'Score']
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

def clean_text(text_df: pd.DataFrame):
    month = text_df[text_df['Text'].str.contains('月')]
    if len(month) > 3 or None:
         raise ValueError("No Month Detected in the Text")

    #Take only the number value for month
    month =  int(month.rpartition('月')[0])

    #Check if it is a premium buffet
    premium = text_df[text_df['Text'].str.contains('プレミアム')]
    if premium != '':
        is_premium = True

    #Check the type of buffet
    if text_df['Text'].str.contains('朝食').any():
        buffet_type = '朝食'
    elif text_df['Text'].str.contains('ランチ').any():
        buffet_type = 'ランチ'
    elif text_df['Text'].str.contains('ディナー').any():
        buffet_type = 'ディナー'
    return month, is_premium, buffet_type
