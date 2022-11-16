from paddleocr import PaddleOCR,draw_ocr
import numpy as np
import pandas as pd

ocr = PaddleOCR(use_angle_cls=True, lang='japan')
img_path = '/Users/bdigio17/Documents/Python_git/Python_ML/nikko_name/menu.jpg'
result = ocr.ocr(img_path, cls=True)
for idx in range(len(result)):
    res = result[idx]
    for line in res:
        print(line)
df=pd.DataFrame(result)


df.head