import json
import os
import shutil
# import fnmatch
import subprocess
import time
import urllib
from urllib.parse import urlparse

from mutagen.mp3 import MP3
import requests

import mysqlUtil
import wget
import platform
import upload
# pip install opencv-python
import cv2
from time import strftime, gmtime
gl_file_list = []
gl_failed_list = []


def fileProcessing(file_path, redirect_url, randomPath):
    pathurl = urlparse(file_path).path
    path_after_oook = pathurl.split("/oook", 1)[1]
    start_time = time.perf_counter()
    path = os.getcwd()
    videocode = 'hevc_amf'
    if platform.system() != 'Windows':
        videocode = 'h264_nvenc'
    new_txt = urllib.parse.unquote(file_path)
    print(new_txt)
    try:
        wget.download(new_txt, path)
    except:
        update_remark("资源异常", randomPath)
        print("资源异常")
        rt = {'code': '500', 'message': '资源异常', 'taskId': randomPath}
        callback(redirect_url, json.dumps(rt))
        return
    filename = os.path.basename(new_txt)
    print(filename)

    sourceFile = os.path.join(path, filename)
    print(sourceFile)
    videopath = os.path.join(path, randomPath)
    if os.path.exists(randomPath):
        shutil.rmtree(videopath)

    os.makedirs(videopath)
    #   # '-c:v', 'hevc_amf',
    #                '-c:v', 'h264_nvenc',
    print("start----------------")
    codePre = "ffmpeg -threads 2 -i "
    # codeMid = " -vcodec h264 "
    # codeMid = " -vcodec libx264 -acodec aac -preset fast -b:v 2000k "
    codeMid = " -vcodec "+videocode+" -acodec aac "
    output_path = os.path.join(videopath, randomPath) + '.mp4'  # 处理后的文件路径
    if (os.path.exists(output_path)):
        os.remove(output_path)
    command = codePre + sourceFile + codeMid + output_path
    if ".mp3" in sourceFile:
        codePre = "ffmpeg -threads 2 -i "
        codeMid = " -c:a mp3 -b:a 128k "
        output_path = os.path.join(videopath, randomPath) + '.mp3'  # 处理后的文件路径
        command = codePre + sourceFile + codeMid + output_path
    print(command)
    # result = os.system(command)
    # if(result != 0):
    #     gl_failed_list.append(file_path)
    #     print(file_name[0], "is failed-----", "result = ", result)
    # else:
    #     print("end------", file_name[0], "result = ", result)

    try:
        retcode = subprocess.call(command, shell=True)
        if retcode == 0:
            print(output_path, "successed------")
            # update当前数据的pdf路径
            duration = get_duration_from_cv2(output_path)
            print(duration)
            v = strftime("%H:%M:%S", gmtime(duration))
            print(v)
            size = os.path.getsize(output_path)  # 获取文件大小（字节）
            print(f"文件大小：{size}字节")
            video_url = upload.upload(output_path, path_after_oook)
            print(video_url)
            mysql = mysqlUtil.MyPymysqlPool("dbMysql")
            update = "UPDATE `ambow_wps`.`file_record` SET `video_url` = '" + video_url + "',`duration` = '" + v  + "',`size` = '" + str(size) + "',`remark` = '转换成功'  WHERE `id` ='" + randomPath + "';"
            print(update)
            result = mysql.update(update)
            print(result)
            # 释放资源
            mysql.dispose()
            shutil.rmtree(videopath)
            # 删源资源
            os.remove(sourceFile)
        else:
            print(output_path, "is failed--------")
            update_remark("转码失败", randomPath)
            print("转码失败")
            rt = {'code': '500', 'message': '转码失败', 'taskId': randomPath}
            callback(redirect_url, json.dumps(rt))
            shutil.rmtree(videopath)
            # 删源资源
            os.remove(sourceFile)
            return
    except Exception as e:
        print("Error:", e)

    print("---------------End all-----------------")
    # 查询 解析回调
    mysql = mysqlUtil.MyPymysqlPool("dbMysql")
    selectById = "SELECT `id`, `file_url`, `pdf_url`, `img_url`,`img_detail`,`video_url`, `duration`,  `img_count`,  `size` FROM `ambow_wps`.`file_record` WHERE `id` = '" + randomPath + "';"
    print(selectById)
    result = mysql.getOne(selectById)
    # print(result)
    # 释放资源
    mysql.dispose()
    if result != False:
        js = json.dumps(result)
        s1 = json.loads(js)
        # print(s1)
        pdf_url = s1['pdf_url']
        img_url = s1['img_url']
        img_detail = s1['img_detail']
        video_url = s1['video_url']
        duration = s1['duration']
        size = s1['size']
        # print(pdf_url)
        # print(img_url)
        rt = {'code': '200', 'message': '任务处理成功', 'taskId': randomPath, 'pdfUrl': pdf_url,
              'imgUrl': img_url, 'imgDetail': img_detail, 'videoUrl': video_url, 'videoDuration': duration, 'size': size}
        callback(redirect_url, json.dumps(rt))

    end_time = time.perf_counter()
    print(f"时间差：{end_time - start_time}")


def callback(url, param):
    headers = {
        'content-type': "application/json;charset=UTF-8"
    }

    response = requests.post(url=url, data=param,
                             headers=headers,
                             verify=True)
    try:
        print("response:" + response.text)
    except:
        pass


def get_duration_from_cv2(filename):
    if ".mp3" in filename:
        audio = MP3(filename)
        length_in_seconds = audio.info.length
        return length_in_seconds
    cap = cv2.VideoCapture(filename)
    if cap.isOpened():
        rate = cap.get(5)
        frame_num = cap.get(7)
        duration = frame_num / rate
        return duration
    return -1


def update_remark(mes, path):
    mysql = mysqlUtil.MyPymysqlPool("dbMysql")
    update = "UPDATE `ambow_wps`.`file_record` SET `remark` = '" + mes + "'  WHERE `id` ='" + path + "';"
    print(update)
    result = mysql.update(update)
    print(result)
    # 释放资源
    mysql.dispose()

# if __name__ == '__main__':
#     start_time = time.perf_counter()
#     file_path = r'z:/mp4/p2526.mp4'
#
#     # fileProcessing(file_path)
#     end_time = time.perf_counter()
#     print(f"时间差：{end_time - start_time}")
