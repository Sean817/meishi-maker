'''
@Software: PyCharm
@File: creat_path.py.py
@Author: PySean
@Time: Jan 05, 2021
'''
import time
import os


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


# basepath = os.path.abspath(os.path.dirname(__file__))
# # print(basepath)
# dir_path = basepath + '/static/moment_pic/'
# print(create_path(dir_path))
