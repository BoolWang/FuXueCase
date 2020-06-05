# -- coding: utf-8 --
# Python推荐使用
#-*- coding:utf-8 -*-
# 简化写法
# encoding: utf-8

"""
通用类和函数
实体类型：Course类
数据处理：ConnectDB类
"""
import pandas as pd
import numpy as np
import pymysql
import sys
sys.path.append(sys.path.append('../'))
from settings import *

class ConnectDB():
    '''
    连接数据库获取数据
    '''
    def mysql(sql):
        '''
        连接mysql数据库获取数据
        :return: 元组类型，例如((’八大浪费',123),('八大浪费',234))
        '''
        db = pymysql.connect(MYSQL_HOST, MYSQL_COUNT, MYSQL_COUNTPW, MYSQL_DB)
        cursor = db.cursor()
        cursor.execute(sql)
        data = cursor.fetchall()
        db.close()
        return data

    def mongo():
        """没实现"""
        pass


class Course():
    '''
    课程相关的属性和方法
    '''
    default = None

    def __init__(self, name=default, courseid=default, exam=default, serialkey=default, creditvalue=default,
                 publishDate=default):
        self.name = name
        self.courseid = courseid
        self.exam = exam
        self.serialkey = serialkey
        self.creditvalue = creditvalue
        self.publishDate = publishDate

    def cour_lable(self):
        '''
        获得课程人气程度分类
        :return: 列表类型，[课程编号，课程类别],例如[[123,0],[234,1]]
        '''
        # 输入可迭代对象，例如：[1234]
        # 读取已经分好类的课程类型
        # courLanleFile = pd.read_csv(r"D:\FUXueCase\fuxuecase\case4\case4_data\course_label.csv")
        if self.courseid is not None:
            courLableFile = pd.read_csv(r"../case4/case4_data/course_lable.csv")
            courLableList = []
            for c in self.courseid:
                if int(c) in courLableFile["courseid"].tolist():
                    courLableList.append([c, courLableFile[courLableFile["courseid"] == int(c)]["label"].iloc[0]])
                else:
                    courLableList.append([c, None])
            return courLableList
        else:
            raise Exception("courseid is necessary")

    def cour_ware(self):
        '''
        获得课程的所有课件编号
        :return: 获得列表类型，[课程编号,课件编号]，例如[[123,001,002],[234,005]]
        '''
        if self.courseid is not None:
            courWareList = []
            for c in self.courseid:
                data = ConnectDB.mysql("select WareId from CourseWare where CourseId=%s" % (c))
                if len(data) > 0:
                    courWareList.append([c, np.array(data)[:, 0].tolist()])
                else:
                    courWareList.append([c, None])
            return courWareList
        else:
            raise Exception("courseid is necessary")
