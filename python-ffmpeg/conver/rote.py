import json
import secrets
import decrypt
from flask import Flask, request, Response
# 注意最新版本再win10上会有问题  gevent	22.10.1	 用这个目前没有发现问题
from gevent import pywsgi

from ReadConfig import ReadConfigFile
from minioremove import removeListFile

app = Flask(__name__)
# app.run(port=8686)
import mysqlUtil
# pip install kafka-python
from kafka import KafkaProducer
from kafka.errors import KafkaError

producer = KafkaProducer(bootstrap_servers=ReadConfigFile().read_config()[4])


# topic = 'wps-test'

# 测试数据
# 加密 https://minio.ambow.com/oook/wps/10%E6%9C%88%E4%BB%BD%E7%9B%B4%E6%92%AD%E6%B1%87%E6%80%BB%E5%90%AB%E5%A4%A7%E9%99%86-%E5%8A%A0%E5%AF%86.xlsx
# https://minio.ambow.com/oook/wps/202208%E9%9B%81%E6%A0%96%E5%B0%8F%E9%95%87%E9%A6%96%E5%BC%80%E5%8C%BA%E6%96%B9%E6%A1%88%E4%BB%8B%E7%BB%8D%EF%BC%88%E5%8A%A0%E5%AF%86%EF%BC%89.pdf
# https://minio.ambow.com/oook/wps/%E5%9B%BD%E9%99%85%E8%83%9C%E4%BB%BB%E5%8A%9B%E7%9A%84%E9%9C%80%E6%B1%82%E5%92%8C%E5%9F%B9%E5%85%BB0406-%E5%8A%A0%E5%AF%86.pptx
# https://minio.ambow.com/oook/wps/%E7%BD%91%E7%BB%9C%E6%91%84%E5%83%8F%E5%A4%B4%EF%BC%88%E5%8A%A0%E5%AF%86%EF%BC%89.docx
# https://minio.ambow.com/oook/wps/%E9%9D%9E%E8%B4%A2%E5%8A%A1%E4%BA%BA%E5%91%98%E8%B4%A2%E5%8A%A1%E7%AE%A1%E7%90%86%E5%9F%B9%E8%AE%AD-%E4%BA%91%E5%8F%B8%E4%BC%9A3%E6%9C%8821%E6%97%A5-%E5%8A%A0%E5%AF%86.ppt
# 未加密 https://minio.ambow.com/oook/wps/%E6%96%B0%E5%BB%BA%20XLSX%20%E5%B7%A5%E4%BD%9C%E8%A1%A8-2141.xlsx
# https://minio.ambow.com/oook/wps/%E5%9B%A0%E6%95%B8%E8%88%87%E9%99%AA%E6%95%B8-%E8%AA%AA%E6%95%B8%E8%A7%A3%E5%AD%97-%E6%8E%92.pptx
# https://minio.ambow.com/oook/wps/OOOKlive2.020220317.docx
# https://minio.ambow.com/oook/wps/%E5%85%83%E5%AE%87%E6%9C%AA%E6%9D%A5%E7%A7%91%E6%8A%80%2B%E4%BB%8B%E7%BB%8D%5B%E6%B1%97%5D%5B%E6%B1%97%5D.pdf
# https://minio.ambow.com/oook/wps/%E9%9D%9E%E8%B4%A2%E5%8A%A1%E4%BA%BA%E5%91%98%E8%B4%A2%E5%8A%A1%E7%AE%A1%E7%90%86%E5%9F%B9%E8%AE%AD-%E4%BA%91%E5%8F%B8%E4%BC%9A3%E6%9C%8821%E6%97%A5.ppt
# 视频 https://minio.ambow.com/oook/wps/10.mpg
@app.route('/', methods=['POST', 'GET'])
def hello_world():
    return 'Hello World!'


@app.route('/conversion', methods=['POST'])
def conversion():
    authentication = request.headers.get("authentication");
    appkey = request.headers.get("appkey")
    if appkey == None or authentication == None:
        res = {'code': '400', 'message': '参数异常'}
        return Response(json.dumps(res), mimetype='application/json')
    print(request.headers.get("authentication"))
    print(request.headers.get("appkey"))
    mysql = mysqlUtil.MyPymysqlPool("dbMysql")
    selectOne = "SELECT * FROM  `account` where id='" + appkey + "'";
    print(selectOne)
    result = mysql.getOne(selectOne)
    if result == False:
        res = {'code': '401', 'message': '无权限'}
        return Response(json.dumps(res), mimetype='application/json')
    print(result)
    js = json.dumps(result)
    s1 = json.loads(js)
    print(s1)
    redirect_url = s1['redirect_url']
    print(redirect_url)
    # 释放资源
    mysql.dispose()
    # 校验传来的加密值是不是有效
    aes_secret_key = s1['aes_secret_key']
    iv = s1['iv']
    try:
        d = decrypt.decrypt(aes_secret_key, authentication, iv)
        h = json.loads(d)
        print(h['t'])  # 时间戳暂时先不做逻辑.
        print(h['key'])
        if h['key'] != appkey:
            res = {'code': '401', 'message': '无权限'}
            return Response(json.dumps(res), mimetype='application/json')
    except:
        res = {'code': '401', 'message': '无权限'}
        return Response(json.dumps(res), mimetype='application/json')

    print(request.json)
    url = request.json['fileUrl']
    try:
        source_type = request.json['sourceType']
    except:
        source_type = 0
    print(url)
    # 写入kafka
    # download.downloadFile(url, redirect_url)
    randomPath = creatId(appkey)
    # 入库当前转档记录
    mysql = mysqlUtil.MyPymysqlPool("dbMysql")
    insert = "INSERT INTO `ambow_wps`.`file_record` (`id`, `file_url`,`app_server`) VALUES ('" + randomPath + "', '" + url + "','" + appkey + "');"
    print(insert)
    result = mysql.insert(insert)
    print(result)
    # 释放资源
    mysql.dispose()
    sendKafka(redirect_url, url, source_type, randomPath)
    rt = {'code': '201', 'message': '任务接受成功', 'taskId': randomPath}

    return Response(json.dumps(rt), mimetype='application/json')


@app.route('/deleteFileList', methods=['POST'])
def deleteFileList():
    authentication = request.headers.get("authentication");
    appkey = request.headers.get("appkey")
    if appkey == None or authentication == None:
        res = {'code': '400', 'message': '参数异常'}
        return Response(json.dumps(res), mimetype='application/json')
    print(request.headers.get("authentication"))
    print(request.headers.get("appkey"))
    mysql = mysqlUtil.MyPymysqlPool("dbMysql")
    selectOne = "SELECT * FROM  `account` where id='" + appkey + "'";
    print(selectOne)
    result = mysql.getOne(selectOne)
    if result == False:
        res = {'code': '401', 'message': '无权限'}
        return Response(json.dumps(res), mimetype='application/json')
    print(result)
    fileList = []
    try:
        id = request.json['id']
        fileList = removeListFile(id)
    except:
        pass
    print(fileList)
    rt = {'code': '200', 'message': '数据删除成功', 'fileList': fileList}
    return Response(json.dumps(rt), mimetype='application/json')


def creatId(appkey):
    randomPath = secrets.token_urlsafe(16)
    randomPath = appkey + randomPath
    # 先查询主键是不是存在.
    mysql = mysqlUtil.MyPymysqlPool("dbMysql")
    selectById = "SELECT * FROM `ambow_wps`.`file_record` WHERE `id` = '" + randomPath + "';"
    print(selectById)
    result = mysql.getOne(selectById)
    print(result)
    # 释放资源
    mysql.dispose()
    if result != False:
        randomPath = creatId(appkey)
    return randomPath


topicmap = {
    'doc': 'wps-test',
    'docx': 'wps-test',
    'ppt': 'wps-test',
    'pptx': 'wps-test',
    'xls': 'wps-test',
    'xlsx': 'wps-test',
    'pdf': 'wps-test',
    'avi': 'video-test',
    'wmv': 'video-test',
    'mkv': 'video-test',
    'mp4': 'video-test',
    'mov': 'video-test',
    'rm': 'video-test',
    '3gp': 'video-test',
    'flv': 'video-test',
    'gif': 'video-test',
    'mpg': 'video-test',
    'rmvb': 'video-test',
    'swf': 'video-test',
    'vob': 'video-test',
    'mp3': 'video-test',
}

# 来源类型：1ok后台手动上传 2okLive直播云端录制 3okLive直播间手动上传 4okLive门户素材手动上传
topicmap_live = {
    'doc': 'wps-live',
    'docx': 'wps-live',
    'ppt': 'wps-live',
    'pptx': 'wps-live',
    'xls': 'wps-live',
    'xlsx': 'wps-live',
    'pdf': 'wps-live',
    'avi': 'video-live',
    'wmv': 'video-live',
    'mkv': 'video-live',
    'mp4': 'video-live',
    'mov': 'video-live',
    'rm': 'video-live',
    '3gp': 'video-live',
    'flv': 'video-live',
    'gif': 'video-live',
    'mpg': 'video-live',
    'rmvb': 'video-live',
    'swf': 'video-live',
    'vob': 'video-live',
    'mp3': 'video-live',
}

# 音频去噪 type 99
topicmap_denosise = {
    # 'mp4': 'denoise-live',
    'wav': 'denoise-live'
}
# 对应的webm转码进入到这个topic
topicmap_translateLiveVideo = {
    # 'mp4': 'denoise-live',
    'webm': 'translateLiveVideo'
}



def sendKafka(redirect_url, url, source_type, randomPath):
    try:
        name_arr = url.split(".")
        suffix = name_arr[len(name_arr) - 1].lower()
        # 判断后缀 区分资源类型给到不同的topic
        topic = topicmap.get(suffix)
        print(source_type)
        # type值为3 说明是直播间的资料
        print(type(source_type) == type(3))
        if source_type == 3:
            topic = topicmap_live.get(suffix)
        # type为99 说明是去噪的音频
        if source_type == 99:
            topic = topicmap_denosise.get(suffix)
        # type为9 说明是要进行转码的的webm
        if source_type == 9:
            topic = topicmap_translateLiveVideo.get(suffix)
        if (topic is None):
            return False

        # 需要处理到哪个topic
        dic = {}
        dic['url'] = url
        dic['redirect_url'] = redirect_url
        dic['randomPath'] = randomPath
        producer.send(topic, json.dumps(dic).encode())
        print("send:" + json.dumps(dic))
        print("sendTopic:" + topic)
    except KafkaError as e:
        print(e)
    finally:
        producer.flush()
        print('done')


server = pywsgi.WSGIServer(('0.0.0.0', 8080), app)
server.serve_forever()
# if __name__ == '__main__':


# app.run()
# randomPath = creatId()
# print(randomPath)
