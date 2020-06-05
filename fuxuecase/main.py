# -- coding: utf-8 --
"""
公用配置
"""


"""
case4配置与常量
"""
MOUDEL_PATH = r"./model/course_modle.ckpt"

# STD_COURSE_DATA，用来做对比的参数
# 目前使用二类受欢迎课程数据作为标准
# 二类受欢迎课程课件是PDF的比例
courWarePDFRate = "68.69%"
# 二类课程平均时长
courAvgTime = 25.9
# 二类课程平均页码数
courAvgPage = 46.7
# 二类课程平均课件数
courAvgWareNum = 2.28
# 二类课程考试课程比例
courExamRate = "62.0%"

STD_COURSE_DATA = {
    'courWarePDFRate' : courWarePDFRate,
    'courAvgTime' : courAvgTime,
    'courAvgPage' : courAvgPage,
    'courAvgWareNum' : courAvgWareNum ,
    'courExamRate' : courExamRate
}
