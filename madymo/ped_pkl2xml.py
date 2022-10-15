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
import joblib
import cv2


# 读取.pkl文件
def pkl_read(path):
    inf = joblib.load(path)

    # print(inf.keys())
    # for k, v in inf[0].items():
    #     print(k, np.shape(v))
    # print(inf[0]["pred_camera"][0])
    return inf


def get_pose_pkl(inf):
    pose_E = []
    pose_R = inf[0]["pose"][0]
    for pose_R_id in pose_R:
        pose_E_id = cv2.Rodrigues(pose_R_id)[0]
        pose_E.append(pose_E_id)
    pose_re = np.array(pose_E).reshape(1, -1)

    global_rot_R = inf[0]["global_orient"][0][0]
    global_rot_E = cv2.Rodrigues(global_rot_R)[0]
    global_rot_E = np.array(global_rot_E).reshape(1, -1)
    # print(global_rot_E[0])

    pose_zeros = np.zeros(72, )  # 创建pose参数初始化
    pose_zeros[0:3] = global_rot_E[0]
    pose_zeros[3:] = pose_re[0]

    pose_str = str(pose_zeros.astype(float))[1:-1]
    pose_line = pose_str.split()
    return pose_line


def h_ped(pkl_path, xml_rest, xml_path):
    print("----------", xml_rest, "----------")
    num = 0
    # 获取ini_path下文件名
    pkl_file_list = os.listdir(pkl_path)
    for pkl_file in pkl_file_list:
        # 获取文件名
        filename, extension = os.path.splitext(pkl_file)
        # 打开.pkl文档
        inf = pkl_read(os.path.join(pkl_path, pkl_file))

        pose_pkl = get_pose_pkl(inf)

        # 打开xml文档(复制）
        xml_file = os.path.join(xml_path, filename+".xml")
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

        ShoulderL_zero = 1.4  # 预先调整的转动角度
        ShoulderR_zero = - 1.4  # 预先调整的转动角度

        # 朝向
        Human = joint_pose[0]
        # Human_R1 = np.array(pose_pkl[1]).astype(np.float)
        # Human_R1 = Human_R1 - np.pi
        # if Human_R1 < -np.pi:
        #     Human_R1 = Human_R1 + 2 * np.pi
        # Human.setAttribute("R1", str(Human_R1))
        # Human.setAttribute("R2", pose_pkl[0])
        # Human.setAttribute("R3", pose_pkl[2])

        Human.setAttribute("R1", '0')
        Human.setAttribute("R2", '0')
        Human.setAttribute("R3", '90')

        # 下脊柱
        LumbarLow = joint_pose[1]
        LumbarLow.setAttribute("R1", pose_pkl[10])
        LumbarLow.setAttribute("R2", pose_pkl[9])
        LumbarLow.setAttribute("R3", pose_pkl[11])

        # 中脊柱
        LumbarUp = joint_pose[2]
        LumbarUp.setAttribute("R1", pose_pkl[20])
        LumbarUp.setAttribute("R2", pose_pkl[18])
        LumbarUp.setAttribute("R3", pose_pkl[19])

        # 上脊柱
        TorsoUp = joint_pose[3]
        pass

        # 脖子
        Neck = joint_pose[4]
        Neck_R2 = np.array(pose_pkl[36]).astype(np.float)
        Neck_R2 = Neck_R2 - 0.3
        Neck.setAttribute("R1", pose_pkl[38])
        Neck.setAttribute("R2", str(Neck_R2))
        Neck.setAttribute("R3", pose_pkl[37])

        # 头
        Head = joint_pose[5]
        Head.setAttribute("R1", pose_pkl[47])
        Head.setAttribute("R2", pose_pkl[45])
        Head.setAttribute("R3", pose_pkl[46])

        # 左肩
        ShoulderL = joint_pose[6]
        ShoulderL_Z = np.array(pose_pkl[50]).astype(np.float)
        ShoulderL_Z = ShoulderL_Z + ShoulderL_zero
        # if ShoulderL_Z > np.pi:
        #     ShoulderL_Z = ShoulderL_Z - np.pi

        ShoulderL.setAttribute("R1", pose_pkl[48])
        ShoulderL.setAttribute("R2", str(ShoulderL_Z))

        # 右肩
        ShoulderR = joint_pose[7]
        ShoulderR_Z = np.array(pose_pkl[53]).astype(np.float)
        ShoulderR_Z = ShoulderR_Z + ShoulderR_zero
        # if ShoulderR_Z < -np.pi:
        #     ShoulderR_Z = ShoulderR_Z + np.pi
        ShoulderR.setAttribute("R1", pose_pkl[51])
        ShoulderR.setAttribute("R2", str(ShoulderR_Z))

        # 左肘
        ElbowL = joint_pose[8]
        ElbowL_R1 = np.array(pose_pkl[54]).astype(np.float)
        ElbowL_R1 = - ElbowL_R1

        ElbowL.setAttribute("R1", str(ElbowL_R1))  # 方向相反
        ElbowL.setAttribute("R2", pose_pkl[55])

        # 右肘
        ElbowR = joint_pose[9]
        ElbowR_R2 = np.array(pose_pkl[58]).astype(np.float)
        ElbowR_R2 = - ElbowR_R2
        ElbowR.setAttribute("R1", pose_pkl[57])
        ElbowR.setAttribute("R2", str(ElbowR_R2))  # 方向相反

        # 左腕
        WristL = joint_pose[10]
        WristL.setAttribute("R1", pose_pkl[60])
        WristL.setAttribute("R2", pose_pkl[62])

        # 右腕
        WristR = joint_pose[11]
        WristR.setAttribute("R1", pose_pkl[63])
        WristR.setAttribute("R2", pose_pkl[65])

        # 左大腿
        HipL = joint_pose[12]
        HipL.setAttribute("R1", pose_pkl[5])
        HipL.setAttribute("R2", pose_pkl[3])
        HipL.setAttribute("R3", pose_pkl[4])

        # 右大腿
        HipR = joint_pose[13]
        HipR.setAttribute("R1", pose_pkl[8])
        HipR.setAttribute("R2", pose_pkl[6])
        HipR.setAttribute("R3", pose_pkl[7])

        # 左小腿
        KneeL = joint_pose[14]
        KneeL.setAttribute("R1", pose_pkl[14])
        KneeL.setAttribute("R2", pose_pkl[12])
        KneeL.setAttribute("R3", pose_pkl[13])

        # 右小腿
        KneeR = joint_pose[15]
        KneeR.setAttribute("R1", pose_pkl[17])
        KneeR.setAttribute("R2", pose_pkl[15])
        KneeR.setAttribute("R3", pose_pkl[16])

        # 左脚踝
        AnkleL = joint_pose[16]
        AnkleL.setAttribute("R1", pose_pkl[22])
        AnkleL.setAttribute("R2", pose_pkl[23])
        AnkleL.setAttribute("R3", pose_pkl[21])

        # 右脚踝
        AnkleR = joint_pose[17]
        AnkleR.setAttribute("R1", pose_pkl[25])
        AnkleR.setAttribute("R2", pose_pkl[26])
        AnkleR.setAttribute("R3", pose_pkl[24])

        # 写入.xml文件
        with open(xml_file, 'w', encoding='utf-8') as f:
            dom.writexml(f, encoding='utf-8')

        num = num + 1
        print("\r" + "h_ped完成进度: %d / %d " % (num, len(pkl_file_list)), end='')
    print(" h_ped has finished")


def main():
    # 确定路径
    pkl_path = "pkl_file"

    # 05百分位女性
    xml_rest_05 = "xml_model/h_ped05el_usr.xml"
    xml_path_05 = "xml_file/h_ped05el_usr"

    # 50百分位男性
    xml_rest_50 = "xml_model/h_ped50el_usr.xml"
    xml_path_50 = "xml_file/h_ped50el_usr"

    h_ped(pkl_path, xml_rest_05, xml_path_05)
    h_ped(pkl_path, xml_rest_50, xml_path_50)


if __name__ == '__main__':
    main()
