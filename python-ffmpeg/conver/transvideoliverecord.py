import os
import secrets
import datetime
import re
import time
from moviepy.video.io.VideoFileClip import VideoFileClip
import requests
import mysqlUtil
import json
import os.path
from pathlib import Path
import subprocess
import upload
import platform

output_options = [
    '-vf', 'blackdetect=d=0.5:pix_th=0.00',
    '-an',
]

# Set start and duration times.
start_time = '00:00:00'
duration_time = '00:00:20'


def translate_mp4(filePath, redirect_url, randomPath):
    remove_expire_file(10)
    videocode = 'hevc_amf'
    if platform.system() != 'Windows':
        videocode = 'h264_nvenc'
    dates = datetime.datetime.now()
    # remove_expire_file(10)
    basename = os.path.basename(filePath)  # 获取文件名，即"60495-54193.webm"
    fileName, ext = os.path.splitext(basename)  # 分离文件名和扩展名，获得("60495-54193", ".webm")
    # 校验源文件是否存在
    if not os.path.exists(filePath):
        print("录制文件本就不存在:" + filePath)
        update_remark("录制文件本就不存在", randomPath)
        rt = {'code': '500', 'message': '录制文件本就不存在', 'taskId': randomPath}
        callback(redirect_url, json.dumps(rt))
        return 'translateMp4-录制文件本就不存在'

    stats = os.stat(filePath)
    fileSize = stats.st_size
    print("录制文件大小:" + str(fileSize))

    if fileSize < 1:
        print("录制文件太小了,实则无效:" + filePath)
        update_remark("录制文件太小了,实则无效", randomPath)
        rt = {'code': '500', 'message': '录制文件太小了,实则无效', 'taskId': randomPath}
        callback(redirect_url, json.dumps(rt))
        return 'translateMp4-录制文件太小了,实则无效'
    filePathMp4 = "Z://mp4/" + fileName + ".mp4"
    if platform.system() != 'Windows':
        filePathMp4 = "/mnt/mp4/" + fileName + ".mp4"

    # 判断文件是否已经存在，如果存在直接返回
    if os.path.exists(filePathMp4):
        print("translateMp4-已存在转换文件:" + filePathMp4)
        update_remark("已存在转换文件", randomPath)
        rt = {'code': '500', 'message': '录制文件太小了,实则无效', 'taskId': randomPath}
        callback(redirect_url, json.dumps(rt))
        return 'translateMp4-已存在转换文件'

    # appDir = os.path.dirname(os.path.abspath(__file__))
    # print("项目路径" + appDir)

    print("转码存储路径" + filePathMp4)
    # 目前 AMD的 hwaccel amf 的参数不生效
    # '-hwaccel', 'cuvid',
    # '-c:v', 'h264_cuvid',  同样执行也存在问题
    ## '-hwaccel', 'nvdec', 他可以用但是没有看出来太大的效果
    # nvdec和cuvid都是FFmpeg中用于GPU硬件加速解码的选项，但它们使用的技术不同。
    # nvdec使用NVDEC（NVIDIA Video Decoder）硬件解码器来将视频流从H.264、HEVC或VP9等格式解码为YUV格式。这个过程在GPU上完成，可以提供更高效的解码性能。但是，在解码之后，还需要使用CPU对图像进行色彩空间转换和缩放等操作。
    # 相比之下，cuvid使用了NVIDIA CUDA技术，它将视频解码器直接移植到GPU中，使解码过程完全在GPU上执行，避免了CPU的参与。这种方法可以进一步提高解码性能，并减少CPU的占用率。
    # 因此，总体而言，cuvid通常比nvdec更快且更节省资源。但是，需要注意的是，cuvid只能在支持CUDA的NVIDIA GPU上运行。
    command = ['ffmpeg',
               # '-hwaccel', 'nvdec',
               # '-hwaccel', 'amf',
               '-i', filePath,
               # '-c:v', 'libx264',
               # '-c:v', 'hevc_amf',
               '-c:v', videocode,
               '-profile:v', 'main',
               '-b:v', '3500k',
               '-r', '29',
               '-c:a', 'aac',
               '-b:a', '128k',
               '-level', '4.0',
               '-threads', '4',
               '-s', '1920x1080',
               '-force_key_frames', 'expr:gte(t,n_forced*4)',
               '-f', 'mp4',
               '-y', filePathMp4]

    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()
        print(out.decode())
        print(err.decode())
        print(filePathMp4, "successed------")
        delBalack(filePathMp4)
        # update当前数据的pdf路径
        duration = get_duration_from_cv2(filePathMp4)
        print(duration)
        v = time.strftime("%H:%M:%S", time.gmtime(duration))
        print(v)
        video_url = upload.uploadLiveRecord(filePathMp4, "/mp4/" + fileName + '.mp4')
        print(video_url)
        stats = os.stat(filePathMp4)
        fileSize = stats.st_size
        mysql = mysqlUtil.MyPymysqlPool("dbMysql")
        update = "UPDATE `ambow_wps`.`file_record` SET `video_url` = '" + video_url + "',`duration` = '" + str(
            v) + "',`size` = '" + str(fileSize) + "',`remark` = '转换成功'  WHERE `id` ='" + randomPath + "';"
        print(update)
        result = mysql.update(update)
        print(result)
        # 释放资源
        mysql.dispose()
        # 删源资源
        os.remove(filePathMp4)

    except Exception as e:
        print('转码Cannot process video: ' + str(e))
        update_remark("转码执行命令失败", randomPath)
        print("转码执行命令失败")
        rt = {'code': '500', 'message': '转码执行命令失败', 'taskId': randomPath}
        callback(redirect_url, json.dumps(rt))
        return str(e)
    datesend = datetime.datetime.now()
    print('转码end Time: ' + str(datesend - dates))
    print("---------------End all-----------------")
    # 查询 解析回调
    mysql = mysqlUtil.MyPymysqlPool("dbMysql")
    selectById = "SELECT `id`, `file_url`, `pdf_url`, `img_url`,`img_detail`,`video_url`, `duration`, `size`,  `img_count` FROM `ambow_wps`.`file_record` WHERE `id` = '" + randomPath + "';"
    print(selectById)
    result = mysql.getOne(selectById)
    # print(result)
    # 释放资源
    mysql.dispose()
    if result != False:
        js = json.dumps(result)
        print(js)
        s1 = json.loads(js)
        # print(s1)
        video_url = s1['video_url']
        duration = s1['duration']
        size = s1['size']
        # print(pdf_url)
        # print(img_url)
        rt = {'code': '200', 'message': '任务处理成功', 'taskId': randomPath, 'fileSize': size, 'videoUrl': video_url,
              'videoDuration': duration}
        callback(redirect_url, json.dumps(rt))


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


def update_remark(mes, path):
    mysql = mysqlUtil.MyPymysqlPool("dbMysql")
    update = "UPDATE `ambow_wps`.`file_record` SET `remark` = '" + mes + "'  WHERE `id` ='" + path + "';"
    print(update)
    result = mysql.update(update)
    print(result)
    # 释放资源
    mysql.dispose()


def get_duration_from_cv2(filename):
    video = VideoFileClip(filename)
    video.close()
    return video.duration  # 获取视频时长（秒）


# Set output file format and options.

def delBalack(inputpath):
    command = [
        'ffmpeg',
        '-i', inputpath,
        '-ss', start_time,
        '-t', duration_time,
        '-vf', output_options[1],
        '-an',
        '-f', "null",
        'pipe:1'
    ]
    print(command)
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()
    black_frames = []
    for line in err.decode().split('\n'):
        # print(line)
        matches = re.search(r'black_start:([0-9\.]+)', line)
        matchesend = re.search(r'black_end:([0-9\.]+)', line)
        if matches:
            timestamp = round(float(matches[1]))
            black_frames.append(timestamp)
        if matches:
            timestampend = round(float(matchesend[1]))
            black_frames.append(timestampend)

    print(f'Black frames found at time(s): {black_frames}')

    # Prepare output file path and name.
    # inputFilePath = inputpath
    parsedPath = Path(inputpath)
    rootDir = parsedPath.parent
    outputFilePath = str(rootDir / (secrets.token_urlsafe(16) + '.mp4'))

    # Crop video.
    blackFrame = black_frames[1] if len(black_frames) > 1 else None
    if blackFrame is None:
        print("我没有黑se")
        return True

    duration = get_duration_from_cv2(inputpath)
    if blackFrame > 0:
        blackFrame = blackFrame + 1
        if blackFrame >= duration:
            print("时长太短,不做操作")
            return True
        print(blackFrame)

    # Crop video using FFmpeg.

    command = [
        'ffmpeg',
        '-i', inputpath,
        '-ss', f'00:00:{blackFrame}',
        '-c', 'copy',
        outputFilePath
    ]
    print(command)
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # Delete original file and rename cropped file.
    # 获取输出和错误信息
    out, err = proc.communicate()

    # 打印输出和错误信息（可选）
    # print(out)
    print(err)
    os.remove(inputpath)
    os.rename(outputFilePath, inputpath)

    print('视频裁剪完成！')
    return True


def remove_expire_file(expire_day):
    try:
        path_data = 'Z://data/'
        if platform.system() != 'Windows':
            path_data = '/mnt/data/'

        filenames = os.listdir(path_data)

        print("\nCurrent directory filenames:")
        for file in filenames:
            print(file)
            created_time = os.path.getctime((path_data + file))
            timestamp = int(time.time() * 1000)
            # print(timestamp)
            # print(info.st_birthtime_ns // 1000000)

            day = (timestamp / 1000 - created_time) / 60 / 60 / 24
            print(day)
            if day > expire_day:
                try:
                    os.remove(path_data + file)
                    print("删除的文件:" + path_data + file)
                except:
                    print("删除的文件不存在了:" + path_data + file)
                    pass

            # print(info)
            # print(day)

    except:
        pass

# if __name__ == '__main__':
#     # translate_mp4("d:\\users\\ruifeng.zhao\\Downloads\\60489-54281.webm", "11", "22")
#     # delBalack("Z://mp4//60495-54193.mp4")
#     remove_expire_file(0)
