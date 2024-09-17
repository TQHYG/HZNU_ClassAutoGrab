import ddddocr
from PIL import Image



def solve_captcha(image_path):
    ocr = ddddocr.DdddOcr()
    # 打开图片
    with open(image_path, 'rb') as image:
        img_bytes = image.read()
    captcha_text = ocr.classification(img_bytes)
    return captcha_text
