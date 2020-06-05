# -- coding: utf-8 --
import tensorflow as tf
import pandas as pd
import numpy as np
import pymysql
import sys
sys.path.append(sys.path.append('../'))  # 导入上一级目录中的包

from settings import *

# 查询课程信息
# 课程信息查询,例：离散数学及其应用
# 课程编号，课程名称，公司企业名称，课程编码，课程类别，学分，是否考试，上传时间，标签
def courInfo(courseName):
    db = pymysql.connect("10.134.149.182", "F3235631", "3235631", "university")
    cursor = db.cursor()
    cursor.execute(
        "select c.CourseId,c.Name,cp.Name,c.SerialKey,cs.Name,c.CreditValue,c.Exam,c.PublishDate,c.Tags from Course as c, Company as cp,CourseSerial as cs where c.Name = '%s' and c.SerialId = cs.SerialId and c.CompanyId = cp.CompanyId" % (
            courseName))
    data = cursor.fetchall()
    return data[0]


# 构建课程分析提建议所需数据
# 模型需要的数据：课程类型，学分，是否考试，课件数量，课件类型，课件时长，pdf页数
def getCourseData(courseid):
    db = pymysql.connect("10.134.149.182", "F3235631", "3235631", "university")
    cursor = db.cursor()
    cursor.execute(
        "select CourseId,SerialId,CreditValue,Exam from Course where Deleted=0 and CourseId= %d" % (courseid))
    data = list(cursor.fetchall()[0])
    cursor.execute("select count(*),Type,avg(Duration),avg(Page) from CourseWare where CourseId= %d" % (courseid))
    # data.append(list(cursor.fetchall()[0]))
    data = data + list(cursor.fetchall()[0])
    db.close()

    dic = {"s1": [0], "s2": [0], "s3": [0], "s4": [0], "s5": [0], "s6": [0], "s7": [0], "s8": [0], "s9": [0],
           "creditvalue": [data[2]],
           "exam": [data[3]],
           "warenum": [data[4]],
           "type_1": [0], "type_2": [0], "type_3": [0],
           "duration": [float(data[6])],
           "page": [float(data[7])]}
    dataDF = pd.DataFrame(dic)

    dataDF[dataDF.columns[data[1] - 1]] = 1
    if data[5] == 'pdf':
        dataDF[dataDF.columns[12]] = 1
    elif data[5] == 'mp4':
        dataDF[dataDF.columns[13]] = 1
    else:
        dataDF[dataDF.columns[14]] = 1

    return dataDF


def multilayer_perceptron(_X, _w1, _w2, _b1, _b2, _wout, _bout):
    """
    计算课程属于各个列别的可能性大小
    :param _X: 待预测课程的数据
    :param _w1: 从模型读入的参数
    :return: 课程属于各个列别的可能性大小
    """
    layer_1 = tf.nn.sigmoid(tf.add(tf.matmul(_X, _w1), _b1))
    layer_2 = tf.nn.sigmoid(tf.add(tf.matmul(layer_1, _w2), _b2))
    return tf.matmul(layer_2, _wout) + _bout


def courPred(data, MOUDEL_PATH):
    """
    读取模型，预测课程类别
    :param data: 待预测课程的数据
    :param MOUDEL_PATH: 模型存储路径
    :return: 预测课程类别0,1,2,3，分别对应报告中课程类别一，二，三，四
             0 —— 一：需改进
             1 —— 二：较受欢迎
             2 —— 四：非常受欢迎，个例
             3 —— 三：非常受欢迎
    """
    data = np.array(data)
    data = data.astype(np.float32)

    tf.reset_default_graph()
    # 允许参数复用 or 判断是否复用了，已经有了就不再重新创建了
    # tf.get_variable_scope().reuse_variables()
    if "w1" not in vars():
        n_hidden_1 = 256
        n_hidden_2 = 128
        n_input = 17
        n_classes = 4
        w1 = tf.Variable(tf.random_normal([n_input, n_hidden_1]), name="w1"),
        w2 = tf.Variable(tf.random_normal([n_hidden_1, n_hidden_2]), name="w2")
        b1 = tf.Variable(tf.random_normal([n_hidden_1]), name="b1")
        b2 = tf.Variable(tf.random_normal([n_hidden_2]), name="b2")
        wout = tf.Variable(tf.random_normal([n_hidden_2, n_classes]), name="wout")
        bout = tf.Variable(tf.random_normal([n_classes]), name="bout")
        saver = tf.train.Saver()
    else:
        pass

    sess = tf.Session()
    saver.restore(sess, MOUDEL_PATH)
    pred = sess.run(multilayer_perceptron(data, w1[0], w2, b1, b2, wout, bout))
    sess.close()
    return pred.argmax()


# 类别为二，三，四：受欢迎
def courWithoutAdvise():
    return "预测课程受欢迎！"


# 类别为一：需改进
# 维度：是否考试，课件类型、课件数量、时长/页数
def courAdvise(data, STD_COURSE_DATA):
    advice = '该课程仍需改进。\n'
    # 考试
    if data['exam'][0] == 0:
        advice += '课程可增加考试，提升学员对课程的参与度。\n'

    # 课件类型
    if data['type_1'][0] == 0:
        advice += "在受欢迎的课程中，有%s的课程使用了pdf类型的课件，建议课程添加pdf课件便于学员学习复习使用。\n" % (STD_COURSE_DATA['courWarePDFRate'])

    # pdf类，课件少，页码数多
    if data['warenum'][0] < STD_COURSE_DATA['courAvgWareNum'] and data['page'][0] > STD_COURSE_DATA['courAvgPage']:
        advice += "在受欢迎课程中，平均课件数量为%s，平均页码数为%s，本课程有%s的课件数量和%s的平均页码数，建议酌情减少每个课件的\
        页数，增加课件数量，便于学员使用碎片化时间学习。\n" % (
            STD_COURSE_DATA['courAvgWareNum'], STD_COURSE_DATA['courAvgPage'], data['warenum'][0], data['page'][0])

    # MP4类，课件少，平均时间长
    if data['warenum'][0] < STD_COURSE_DATA['courAvgWareNum'] and data['duration'][0] > STD_COURSE_DATA['courAvgTime']:
        advice += "在受欢迎课程中，平均课件数量为%s，视频课程平均时长为%s，本课程有%s个课件数量，每个课件平均时长%s分钟，建议酌情减少每个课件的\
        时长，增加课件数量，便于学员使用碎片化时间学习。\n" % (
            STD_COURSE_DATA['courAvgWareNum'], STD_COURSE_DATA['courAvgTime'], data['warenum'][0],
            round(data['duration'][0] / 60))

    if len(advice) < 10:
        advice = '暂无改进建议'

    return advice

def getAdvise(courseid):
    data = getCourseData(courseid)
    # 2.2 预测课程是否受欢迎
    courTypePred = courPred(data, MOUDEL_PATH)
    # 2.3 如果是受欢迎的类别or不受欢迎的类别分别调用不同函数
    if courTypePred != 0:
        advice = courWithoutAdvise()
    else:
        advice = courAdvise(data, STD_COURSE_DATA)
    return advice


if __name__ == '__main__':
    # 1、查询课程基本信息
    courBasicInfo = courInfo('离散数学及其应用')
    print(courBasicInfo)
    # 2、获得改进建议
    # 2.1 获得需要分析的课程的数据
    data = getCourseData(9477)
    # 2.2 预测课程是否受欢迎
    courTypePred = courPred(data, MOUDEL_PATH)
    # 2.3 如果是受欢迎的类别or不受欢迎的类别分别调用不同函数
    if courTypePred != 0 :
        advice = courWithoutAdvise()
    else :
        advice = courAdvise(data, STD_COURSE_DATA)
    print(advice)
