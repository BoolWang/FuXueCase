# -- coding: utf-8 --
from case4 import *

# 与前端接口未定，暂时使用input测试
# coursename传入的参数字符串
# courseid传入数字

if __name__ == '__main__':
    coursename = input()  #例子：离散数学及其应用
    courseid = input()  # 例子：9477

    courBasicInfo = courInfo(coursename)
    print(courBasicInfo)

    advice = getAdvise(courseid)
    print(advice)
