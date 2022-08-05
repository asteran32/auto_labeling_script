import os
import sys
import shutil
import argparse
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument('--dataset', required=True, help='dataset dir path')

output_dir = './split_output'
precent = 10 # train : 90% test: 10%

train_csv = []
test_csv = []

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

def split_images(dir_num, img_list):
    '''
    Split a dataset
    '''
    for i, img in enumerate(img_list):
        if img.split('.')[-1] == 'png':
            if i % precent == 0: # save test
                test_csv.append(os.path.join(dir_num, img))
            else : # save train
                train_csv.append(os.path.join(dir_num, img))

def copy_img_list(src_dir, dst_dir, img_list):
    '''
    Copy img
    '''
    imgLen = len(img_list)
    for idx, img in enumerate(img_list):
        progress_bar(idx, imgLen)
        src = os.path.join(src_dir, img)
        dst = os.path.join(dst_dir, img)
        shutil.copyfile(src, dst)
    print('\n')
        
def save_as_csv(path, img_list):
    '''
    Save image list as csv file
    '''
    return np.savetxt(path, img_list, delimiter=',', fmt='%s')

if __name__ == '__main__':
    args = parser.parse_args()
    dataset_dir = args.dataset

    print('Dataset directory is %s' %dataset_dir)
    if not os.path.exists(dataset_dir):
        print('Fail to read Dataset directory')
        sys.exit()
    
    # make dirs
    print('Make output directory : %s ... ' %output_dir)
    make_dirs(output_dir)

    train_dirs = os.path.join(output_dir, 'train')
    print('Make output directory : %s ... ' %train_dirs)
    make_dirs(train_dirs)
    for i in range(10):
        make_dirs(os.path.join(train_dirs, str(i)))

    test_dirs = os.path.join(output_dir, 'test')
    print('Make output directory : %s ... ' %test_dirs)
    make_dirs(test_dirs)
    for i in range(10):
        make_dirs(os.path.join(test_dirs, str(i)))

    # split a dataset to train and test
    for num in range(10):
        img_list = os.listdir(os.path.join(dataset_dir, str(num)))
        split_images(str(num), img_list)
    
    # save csv file
    save_as_csv(os.path.join(output_dir, 'train.csv'), train_csv)
    save_as_csv(os.path.join(output_dir, 'test.csv'), test_csv)
        
    # copy file
    print('Split train dataset ... ')
    copy_img_list(dataset_dir, train_dirs, train_csv)
    print('Split test dataset ... ')
    copy_img_list(dataset_dir, test_dirs, test_csv)
