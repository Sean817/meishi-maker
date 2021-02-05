'''
@Software: PyCharm
@File: creat_path.py.py
@Author: PySean
@Time: Jan 05, 2021
'''
import time
import os

import PIL

from PIL import Image
from config import config
from flask_uploads import UploadSet, configure_uploads, IMAGES

photos = UploadSet('photos', IMAGES)
def create_path(dir_path):
    year = time.strftime('%Y', time.localtime(time.time()))
    month = time.strftime('%m', time.localtime(time.time()))
    day = time.strftime('%d', time.localtime(time.time()))
    fileYear = year
    fileMonthDay = fileYear + '/' + month + '-' + day + '/'
    if not os.path.exists(dir_path + fileYear):
        os.mkdir(dir_path + year)
        os.mkdir(dir_path + fileYear + '/' + month + '-' + day)
    else:
        if not os.path.exists(dir_path + fileYear + '/' + month + '-' + day):
            os.mkdir(dir_path + fileYear + '/' + month + '-' + day)

    return fileMonthDay



def create_thumbnail(image):
    filename, ext = os.path.splitext(image)
    base_width = 300
    img = Image.open(photos.path(image))  # # 从上传集获取path
    if img.size[0] <= 300:  # 如果图片宽度小于300，不作处理
        return photos.url(image)  # 从上传集获取url
    w_percent = (base_width / float(img.size[0]))
    h_size = int((float(img.size[1]) * float(w_percent)))
    img = img.resize((base_width, h_size), PIL.Image.ANTIALIAS)
    img.save(os.path.join(current_app.config['UPLOADED_PHOTOS_DEST'], filename+'_t' + ext))
    return url_for('.uploaded_file', filename=filename + '_t' + ext)

# basepath = os.path.abspath(os.path.dirname(__file__))
# # print(basepath)
# dir_path = basepath + '/static/moment_pic/'
# print(create_path(dir_path))
