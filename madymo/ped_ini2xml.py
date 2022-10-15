# -*- coding = utf-8 -*-
# @time:2021/5/10 21:34
# Author:wmj
# @File:ini2xml.py
# @Software:PyCharm
# @Function:MADYMO假人模型数据处理

# coding=utf-8
import xml.dom.minidom
import shutil
import configparser
import os
import numpy as np
import time


def create_folder(filename):
    if os.path.exists(filename):
        pass
    else:
        os.mkdir(filename)


def h_ped(ini_path, xml_rest, xml_path):
    num = 0
    # 获取ini_path下文件名
    ini_file_list = os.listdir(ini_path)
    for ini_file in ini_file_list:
        # 获取文件名
        t0 = time.time()
        filename, extension = os.path.splitext(ini_file)

        # 打开.ini文档
        rest = configparser.ConfigParser()
        rest.read(os.path.join(ini_path, ini_file), encoding='utf-8')
        sections = rest.sections()

        pose_ini = rest.get(sections[0], 'pose')
        pose_ini = pose_ini.split(",")

        # 打开xml文档(复制）
        xml_file = os.path.join(xml_path, filename + ".xml")
        create_folder(xml_path)
        shutil.copy(xml_rest, xml_file)
        dom = xml.dom.minidom.parse(xml_file)

        # 得到.xml文档元素对象
        root = dom.documentElement
        # print(root)
        # print(root.nodeName)
        # print(root.nodeValue)
        # print(root.nodeType)
        # print(root.ELEMENT_NODE)

        # 得到关节“节点”
        joint_pose = root.getElementsByTagName('INITIAL.JOINT_POS')
        # print(len(joint_pose))

        Shoulder_zero = 1.6  # 预先调整的转动角度
        Shoulder_Pr = Shoulder_zero / np.pi + 1

        # 朝向
        Human = joint_pose[0]
        # Human_R1 = np.array(pose_ini[1]).astype(np.float)
        # Human_R1 = Human_R1 - np.pi
        # if Human_R1 < -np.pi:
        #     Human_R1 = Human_R1 + 2 * np.pi
        # Human.setAttribute("R1", str(Human_R1))
        # Human.setAttribute("R2", pose_ini[0])
        # Human.setAttribute("R3", pose_ini[2])

        Human.setAttribute("R1", '0')
        Human.setAttribute("R2", '0')
        Human.setAttribute("R3", '0')

        # 下脊柱
        LumbarLow = joint_pose[1]
        LumbarLow.setAttribute("R1", pose_ini[10])
        LumbarLow.setAttribute("R2", pose_ini[9])
        LumbarLow.setAttribute("R3", pose_ini[11])

        # 中脊柱
        LumbarUp = joint_pose[2]
        LumbarUp.setAttribute("R1", pose_ini[20])
        LumbarUp.setAttribute("R2", pose_ini[18])
        LumbarUp.setAttribute("R3", pose_ini[19])

        # 上脊柱
        TorsoUp = joint_pose[3]
        pass

        # 脖子
        Neck = joint_pose[4]
        Neck_R2 = np.array(pose_ini[36]).astype(np.float)
        Neck_R2 = Neck_R2 - 0.3
        Neck.setAttribute("R1", pose_ini[38])
        Neck.setAttribute("R2", str(Neck_R2))
        Neck.setAttribute("R3", pose_ini[37])

        # 头
        Head = joint_pose[5]
        Head.setAttribute("R1", pose_ini[47])
        Head.setAttribute("R2", pose_ini[45])
        Head.setAttribute("R3", pose_ini[46])

        # 左肩
        ShoulderL = joint_pose[6]
        ShoulderL_Z = np.array(pose_ini[50]).astype(np.float)
        ShoulderL_Z = ShoulderL_Z + Shoulder_zero
        if ShoulderL_Z > np.pi:
            ShoulderL_Z = ShoulderL_Z - Shoulder_Pr * np.pi

        ShoulderL.setAttribute("R1", pose_ini[48])
        ShoulderL.setAttribute("R2", str(ShoulderL_Z))

        # 右肩
        ShoulderR = joint_pose[7]
        ShoulderR_Z = np.array(pose_ini[53]).astype(np.float)
        ShoulderR_Z = ShoulderR_Z - Shoulder_zero
        if ShoulderR_Z < -np.pi:
            ShoulderR_Z = ShoulderR_Z + Shoulder_Pr * np.pi
        ShoulderR.setAttribute("R1", pose_ini[51])
        ShoulderR.setAttribute("R2", str(ShoulderR_Z))

        # 左肘
        ElbowL = joint_pose[8]
        ElbowL_R1 = np.array(pose_ini[54]).astype(np.float)
        ElbowL_R1 = - ElbowL_R1

        ElbowL.setAttribute("R1", str(ElbowL_R1))  # 方向相反
        ElbowL.setAttribute("R2", pose_ini[55])

        # 右肘
        ElbowR = joint_pose[9]
        ElbowR_R2 = np.array(pose_ini[58]).astype(np.float)
        ElbowR_R2 = - ElbowR_R2
        ElbowR.setAttribute("R1", pose_ini[57])
        ElbowR.setAttribute("R2", str(ElbowR_R2))  # 方向相反

        # 左腕
        WristL = joint_pose[10]
        WristL.setAttribute("R1", pose_ini[60])
        WristL.setAttribute("R2", pose_ini[62])

        # 右腕
        WristR = joint_pose[11]
        WristR.setAttribute("R1", pose_ini[63])
        WristR.setAttribute("R2", pose_ini[65])

        # 左大腿
        HipL = joint_pose[12]
        HipL.setAttribute("R1", pose_ini[5])
        HipL.setAttribute("R2", pose_ini[3])
        HipL.setAttribute("R3", pose_ini[4])

        # 右大腿
        HipR = joint_pose[13]
        HipR.setAttribute("R1", pose_ini[8])
        HipR.setAttribute("R2", pose_ini[6])
        HipR.setAttribute("R3", pose_ini[7])

        # 左小腿
        KneeL = joint_pose[14]
        KneeL.setAttribute("R1", pose_ini[14])
        KneeL.setAttribute("R2", pose_ini[12])
        KneeL.setAttribute("R3", pose_ini[13])

        # 右小腿
        KneeR = joint_pose[15]
        KneeR.setAttribute("R1", pose_ini[17])
        KneeR.setAttribute("R2", pose_ini[15])
        KneeR.setAttribute("R3", pose_ini[16])

        # 左脚踝
        AnkleL = joint_pose[16]
        AnkleL.setAttribute("R1", pose_ini[22])
        AnkleL.setAttribute("R2", pose_ini[23])
        AnkleL.setAttribute("R3", pose_ini[21])

        # 右脚踝
        AnkleR = joint_pose[17]
        AnkleR.setAttribute("R1", pose_ini[25])
        AnkleR.setAttribute("R2", pose_ini[26])
        AnkleR.setAttribute("R3", pose_ini[24])

        # 写入.xml文件
        with open(xml_file, 'w', encoding='utf-8') as f:
            dom.writexml(f, encoding='utf-8')

        num = num + 1
        print("\r" + "h_ped完成进度: %d / %d " % (num, len(ini_file_list)), end='')
        # t1 = time.time()
        # print(ini_file, t1 - t0)

    print("-" * 10, "{} has finished".format(xml_path), "\n")


def main():
    # 确定路径
    ini_path = "ini_file"

    # 05百分位女性
    xml_rest_05 = "xml_model/h_ped05el_usr.xml"
    xml_path_05 = "xml_file/h_ped05el_usr"

    # 50百分位男性
    xml_rest_50 = "xml_model/h_ped50el_usr.xml"
    xml_path_50 = "xml_file/h_ped50el_usr"

    # 95百分位男性
    xml_rest_95 = "xml_model/h_ped95el_usr.xml"
    xml_path_95 = "xml_file/h_ped95el_usr"

    # 6百分位儿童
    xml_rest_06 = "xml_model/h_ped6yel_usr.xml"
    xml_path_06 = "xml_file/h_ped6yel_usr"

    # 3百分位儿童
    xml_rest_03 = "xml_model/h_ped3yel_usr.xml"
    xml_path_03 = "xml_file/h_ped3yel_usr"

    # 50百分位行人+car
    xml_rest_50_car = "xml_model/e_ped50el.xml"
    xml_path_50_car = "xml_file/e_ped50el"

    h_ped(ini_path, xml_rest_03, xml_path_03)
    h_ped(ini_path, xml_rest_06, xml_path_06)
    h_ped(ini_path, xml_rest_05, xml_path_05)
    h_ped(ini_path, xml_rest_50, xml_path_50)
    h_ped(ini_path, xml_rest_95, xml_path_95)

    h_ped(ini_path, xml_rest_50_car, xml_path_50_car)


if __name__ == '__main__':
    main()
