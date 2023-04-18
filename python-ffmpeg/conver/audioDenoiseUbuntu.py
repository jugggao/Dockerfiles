#!/usr/bin/env python
# coding: utf-8

# # 针对影片去噪去回声后切成片段做ASR与分类及摘要处理

# In[1]:


import os, stat
import secrets
from moviepy.video.io.VideoFileClip import VideoFileClip
import cv2
import ffmpeg
# import matplotlib.pyplot as plt
# import numpy as np
import wget
# import torch
import gc
import time
import urllib
import mysqlUtil
import requests
import json
import upload
# import numpy as np
# Import audio processing library
# import librosa
# We'll use this to listen to audio
# from IPython.display import Audio, display
import shutil
from urllib.parse import urlparse
from time import strftime, gmtime


# ## 从ffmpeg的来源取地wave(pcm16)檔

# In[2]:

def audioDenoise(file_url, redirect_url, randomPath):
    start_time = time.perf_counter()
    path = os.getcwd()

    new_txt = urllib.parse.unquote(file_url)
    print(new_txt)
    try:
        print('下载文件开始')
        wget.download(new_txt, path)
        print('下载文件结束')
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

    ar = 16000
    # pathName = '/home/developer/mysamples/demo/'
    audioSdkpath = '/home/sysadmin/'

    print('分离文件开始')
    # print("ffmpeg -i "+pathName + 'video/' + sourcefile+" 2>&1 | grep Video: | grep -Po '\d{3,5}x\d{3,5}' | cut -d'x' -f2")

    input = ffmpeg.input(sourceFile)
    #     audio = input.audio.filter('highpass',200).filter('lowpass',3000).filter('afftdn',nf=-25)
    audio = input.audio
    video = input.video
    ffmpeg.output(audio, videopath + '/' + randomPath + '.wav', format='wav', acodec='pcm_s16le', ac=1, ar=ar).run(
        capture_stdout=True, capture_stderr=True)
    ffmpeg.output(video, videopath + '/' + randomPath + '.mp4', vcodec='libx264').run(capture_stdout=True,
                                                                                      capture_stderr=True)
    print('分离文件结束')

    # # ## 使用Maxine的VideoEffect处理去噪与超解析度成像(Super-resolution),以提升画质
    #
    # # In[ ]:

    # ## 依照抓取的音檔产生Audio Effect的Config檔

    # In[ ]:

    print('生成去噪文件')
    afxfile = open(videopath + '/' + randomPath + '.txt', 'w+')
    afxfile.write('effect dereverb_denoiser\n')
    afxfile.write('sample_rate 16000\n')
    afxfile.write('model ' + audioSdkpath + 'Audio_Effects_SDK/models/sm_86/dereverb_denoiser_16k_3072.trtpkg\n')
    afxfile.write('real_time 0\n')
    afxfile.write('intensity_ratio 1.0\n')
    afxfile.write('input_wav_list  ' + videopath + '/' + randomPath + '.wav\n')
    afxfile.write('output_wav_list ' + videopath + '/' + randomPath + '_out.wav\n')
    afxfile.close()
    print('生成去噪文件结束')
    # ## 使用Maxine的AudioEffect处理回声与背景噪音,以达到录音室等级品质

    # In[ ]:

    print('执行去噪')
    os.system(
        audioSdkpath + 'Audio_Effects_SDK/samples/effects_demo/effects_demo -c ' + videopath + '/' + randomPath + '.txt')
    print('执行去噪结束')
    #

    # ## 删除不需要的组态檔与音檔

    # input_video = ffmpeg.input(pathName + 'video/' + audiofile + '.mp4')
    input_video = ffmpeg.input(videopath + '/' + randomPath + '.mp4')
    # 视频增强生成的文件
    input_audio = ffmpeg.input(videopath + '/' + randomPath + '_out.wav')
    # input_audio = ffmpeg.input(pathName + 'audio/' + audiofile + '.wav')
    # 执行完 覆盖源文件
    if os.path.exists(videopath + '/out_' + filename):
        os.remove(videopath + '/out_' + filename)
    outputFilePath = videopath + '/out_' + filename
    output = ffmpeg.output(input_video, input_audio, outputFilePath, vcodec='copy', acodec='aac',
                           audio_bitrate='128k')
    print('合成文件命令：', ffmpeg.get_args(output))
    # os.remove(sourcefile)
    # print('删除源文件')
    print('执行处理后视频合成开始')
    run = ffmpeg.run(output, capture_stdout=True, capture_stderr=True)
    print('执行处理后视频合成结束')
    print('删除残余文件开始')
    # 进行上传处理
    duration = get_duration_from_cv2(outputFilePath)
    print(duration)
    v = strftime("%H:%M:%S", gmtime(duration))
    print(v)
    size = os.path.getsize(outputFilePath)  # 获取文件大小（字节）
    print(f"文件大小：{size}字节")
    video_url = upload.uploadDenoise(outputFilePath, randomPath, "audio")
    print(video_url)
    mysql = mysqlUtil.MyPymysqlPool("dbMysql")
    update = "UPDATE `ambow_wps`.`file_record` SET `video_url` = '" + video_url + "',`duration` = '" + v + "',`size` = '" + str(
        size) + "',`remark` = '去噪成功'  WHERE `id` ='" + randomPath + "';"
    print(update)
    result = mysql.update(update)
    print(result)
    # 释放资源
    mysql.dispose()

    # In[ ]:

    if os.path.exists(videopath + '/' + randomPath + '.wav'):
        try:
            shutil.rmtree(videopath)
            os.remove(sourceFile)
        except:
            pass
        print('Successfully! The File has been removed')
    else:
        print('Can not delete the file as it doesn\'t exists')
    print('删除残余文件结束')
    # ## 清除GPU资源
    gc.collect()
    print("---------------End all-----------------")
    # In[ ]:
    # 查询 解析回调
    mysql = mysqlUtil.MyPymysqlPool("dbMysql")
    selectById = "SELECT `id`, `file_url`, `pdf_url`, `img_url`,`img_detail`,`video_url`, `duration`,  `img_count` ,  `size` FROM `ambow_wps`.`file_record` WHERE `id` = '" + randomPath + "';"
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
              'imgUrl': img_url, 'imgDetail': img_detail, 'videoUrl': video_url, 'videoDuration': duration,
              'size': size}
        print(rt)
        callback(redirect_url, json.dumps(rt))
    endtime = time.time()
    print('视频处理结束')
    print('总时间执行结束：', (endtime - start_time))
    # Clear up memory
    # torch.cuda.empty_cache()


def audioWavDenoise(file_url, redirect_url, randomPath):
    start_time = time.perf_counter()
    file_extension = os.path.splitext(file_url)[1]  # 获取文件扩展名
    if file_extension.lower() != ".wav":
        update_remark("资源异常不是.wav文件,文件格式:" + file_extension, randomPath)
        print("资源异常不是.wav文件,文件格式:" + file_extension)
        rt = {'code': '500', 'message': '资源异常.wav文件,文件格式:' + file_extension, 'taskId': randomPath}
        callback(redirect_url, json.dumps(rt))
        return
    path = os.getcwd()
    audioSdkpath = '/home/developer/'
    audioFolderpath = os.path.join(path, randomPath)
    if os.path.exists(randomPath):
        shutil.rmtree(audioFolderpath)
    os.makedirs(audioFolderpath)
    if file_url.startswith("http"):
        new_txt = urllib.parse.unquote(file_url)
        print(new_txt)
        try:
            print('下载文件开始')
            wget.download(new_txt, audioFolderpath)
            print('下载文件结束')
        except:
            update_remark("资源异常", randomPath)
            print("资源异常")
            rt = {'code': '500', 'message': '资源异常', 'taskId': randomPath}
            callback(redirect_url, json.dumps(rt))
            return
        filename = os.path.basename(new_txt)
        print(filename)
        audioPath = os.path.join(path, filename)
        print(audioPath)
        outputAudio = audioFolderpath + '/' + randomPath + '_out.wav'
        # ar = 16000
        # pathName = '/home/developer/mysamples/demo/'

        # print('分离文件开始')
        # print("ffmpeg -i "+pathName + 'video/' + sourcefile+" 2>&1 | grep Video: | grep -Po '\d{3,5}x\d{3,5}' | cut -d'x' -f2")

        # input = ffmpeg.input(sourceFile)
        #     audio = input.audio.filter('highpass',200).filter('lowpass',3000).filter('afftdn',nf=-25)
        # audio = input.audio
        # ffmpeg.output(audio, audioPath, format='wav', acodec='pcm_s16le', ac=1, ar=ar).run(
        #     capture_stdout=True, capture_stderr=True)
        # print('分离文件结束')
    else:
        audioPath = file_url
        outputAudio = os.path.dirname(file_url) + '/' + randomPath + '_out.wav'
    # # ## 使用Maxine的VideoEffect处理去噪与超解析度成像(Super-resolution),以提升画质
    #
    # # In[ ]:

    # ## 依照抓取的音檔产生Audio Effect的Config檔

    # In[ ]:

    print('生成去噪文件')
    afxfile = open(audioFolderpath + '/' + randomPath + '.txt', 'w+')
    afxfile.write('effect dereverb_denoiser\n')
    afxfile.write('sample_rate 16000\n')
    afxfile.write('model ' + audioSdkpath + 'Audio_Effects_SDK/models/sm_86/dereverb_denoiser_16k_3072.trtpkg\n')
    afxfile.write('real_time 0\n')
    afxfile.write('intensity_ratio 1.0\n')
    afxfile.write('input_wav_list  ' + audioPath + '\n')
    afxfile.write('output_wav_list ' + outputAudio + '\n')
    afxfile.close()
    print('生成去噪文件结束')
    # ## 使用Maxine的AudioEffect处理回声与背景噪音,以达到录音室等级品质

    # In[ ]:

    print('执行去噪')
    os.system(
        audioSdkpath + 'Audio_Effects_SDK/samples/effects_demo/effects_demo -c ' + audioFolderpath + '/' + randomPath + '.txt')
    print('执行去噪结束')
    #
    # ## 清除GPU资源
    gc.collect()
    print("---------------End all-----------------")
    # ## 删除不需要的组态檔与音檔

    # print('删除源文件')
    print('删除残余文件开始')
    # 进行上传处理
    try:
        video_url = upload.uploadDenoise(outputAudio, randomPath, "audio")
    except Exception as e:
        print(e)
        errormsg = str(e).replace("'", "")
        update_remark(errormsg, randomPath)
        rt = {'code': '500', 'message': '资源异常:' + errormsg, 'taskId': randomPath}
        callback(redirect_url, json.dumps(rt))
        return

    print(video_url)
    mysql = mysqlUtil.MyPymysqlPool("dbMysql")
    update = "UPDATE `ambow_wps`.`file_record` SET `video_url` = '" + video_url + "',`remark` = '去噪成功'  WHERE `id` ='" + randomPath + "';"
    print(update)
    result = mysql.update(update)
    print(result)
    # 释放资源
    mysql.dispose()

    # In[ ]:

    if os.path.exists(audioFolderpath + '/' + randomPath + '.wav'):
        try:
            shutil.rmtree(audioFolderpath)
        except:
            pass
        print('Successfully! The File has been removed')
    else:
        print('Can not delete the file as it doesn\'t exists')
    print('删除残余文件结束')

    # In[ ]:
    # 查询 解析回调
    mysql = mysqlUtil.MyPymysqlPool("dbMysql")
    selectById = "SELECT `video_url` FROM `ambow_wps`.`file_record` WHERE `id` = '" + randomPath + "';"
    print(selectById)
    result = mysql.getOne(selectById)
    # print(result)
    # 释放资源
    mysql.dispose()
    if result != False:
        js = json.dumps(result)
        s1 = json.loads(js)
        # print(s1)
        video_url = s1['video_url']
        # print(pdf_url)
        # print(img_url)
        rt = {'code': '200', 'message': '任务处理成功', 'taskId': randomPath, 'audioUrl': video_url,
              'audioPath': outputAudio}
        print(rt)
        callback(redirect_url, json.dumps(rt))
    endtime = time.time()
    print('视频处理结束')
    print('总时间执行结束：', (endtime - start_time))
    # Clear up memory
    # torch.cuda.empty_cache()


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
    video = VideoFileClip(filename)
    return video.duration  # 获取视频时长（秒）


def update_remark(mes, path):
    mysql = mysqlUtil.MyPymysqlPool("dbMysql")
    update = "UPDATE `ambow_wps`.`file_record` SET `remark` = '" + mes + "'  WHERE `id` ='" + path + "';"
    print(update)
    result = mysql.update(update)
    print(result)
    # 释放资源
    mysql.dispose()


if __name__ == '__main__':
    audioDenoise('https://dev-vod.oook.cn/video/user/2067409/mp4/20230308/30843-2237.mp4', "cc", "45678293046985743")
