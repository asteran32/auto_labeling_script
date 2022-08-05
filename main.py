import os
import sys
import cv2
import easyocr
import argparse
import random
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument('--dataset', required=True, help='dataset dir path')

output_dir = './output'

def progress_bar(count, total, suffix=''):
    barLength = 60
    filedLegth = int(round(barLength * count / float(total)))
    percent = round(100.0 * count / float(total), 1)
    bar = '=' * filedLegth + '-' *(barLength - filedLegth)

    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percent, '%', suffix))
    sys.stdout.flush()

def make_dirs(output):
    '''
    Check path and make dirs
    '''
    if not os.path.exists(output):
        os.mkdir(output)

def preprocessing(img):
    '''
    Image processing for contouring
    '''
    src = cv2.imread(img, cv2.IMREAD_GRAYSCALE)
    dst = cv2.blur(src, (3,3))
    dst = cv2.adaptiveThreshold(dst, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 5, 3)
    dst = cv2.dilate(dst, cv2.getStructuringElement(cv2.MORPH_CROSS, (3,3)), 1)
    return dst

def detect_region(img):
    '''
    Detect digits text region
    '''
    rect = []
    try:    
        dst = preprocessing(img)
        contours, _ = cv2.findContours(dst, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    except:
        print('can not read img, img is None')
    else:
        for c in contours:
            x, y, w, h = cv2.boundingRect(c)
            if w > 10 and h > 20:
                rect.append([x, y, w, h])
    return rect

def crop_image_and_save(img, class_num):
    '''
    Crop digits image and save the image
    '''
    timestr = datetime.now().strftime('%Y%m%d%H%M')
    rand_id = random.randint(0,1000000)
    f_name = "img_"
    f_name += timestr + '_'
    f_name += str(rand_id) + '.png'
    dir_path = os.path.join(output_dir, str(class_num))
    cv2.imwrite(os.path.join(dir_path, f_name), img)

def run_ocr(contours, img):
    '''
    Run easyocr digits only
    '''
    pad = 4
    src = cv2.imread(img, cv2.IMREAD_GRAYSCALE)
    dst = preprocessing(img)
    for c in contours:
        x, y, w, h = c
        crop = dst[y-pad:y+h+pad, x-pad:x+w+pad]
        try:
            results = reader.readtext(crop, allowlist="0123456789") # only digits
        except:
            continue
        else:
            if len(results) == 0:
                continue
            _results_class = results[0][-2]
            _results_prob = results[0][-1]
            if _results_prob > 0.5:
                # 3가지 padding으로 이미지를 저장
                for i in range(3):
                    gray_crop = src[y-i:y+h+i, x-i:x+w+i]
                    crop_image_and_save(gray_crop, _results_class)
            
if __name__ == '__main__':
    args = parser.parse_args()
    dataset_dir = args.dataset

    if not os.path.exists(dataset_dir):
        print('Fail to read Dataset directory')
        sys.exit()
    
    # Load easyocr reader english only mode
    reader = easyocr.Reader(["en"])

    # check dirs
    ds_dirlist = [i for i in os.listdir(dataset_dir) if i != '.DS_Store']

    # make output dirs
    make_dirs(output_dir)
    for i in range(10):
        make_dirs(os.path.join(output_dir, str(i)))

    # check image and run ocr
    for dir in ds_dirlist:
        dir_path = os.path.join(dataset_dir, dir)
        img_list = [img for img in os.listdir(dir_path) if img.split('.')[-1] == 'png'] # only png
        
        print('Start labeling ... %s directory' %dir_path)
        img_total = len(img_list)
        for i, img in enumerate(img_list):
            progress_bar(i, img_total)
            img_path = os.path.join(dir_path, img)
            contours = detect_region(img_path)
            if len(contours) == 0:
                continue
            run_ocr(contours, img_path)
        print('\n')
    