import os
from xmlrpc.client import ResponseError

from minio import Minio
from minio.commonconfig import CopySource

from ReadConfig import ReadConfigFile


def upload(file, path):
    # 使用endpoint、access key和secret key来初始化minioClient对象。
    minioClient = Minio(ReadConfigFile().read_config()[0],
                        access_key=ReadConfigFile().read_config()[2],
                        secret_key=ReadConfigFile().read_config()[3],
                        secure=True)

    # 调用make_bucket来创建一个存储桶。
    # filename = os.path.basename(file)
    # miniopath = '/wps/' + path + "/" + type + "/" + filename
    try:
        directory = path.rsplit("/", 1)[0] + "/"  # 获取目录部分，即 /user/2138501/mp4/20230328/
        print(directory)
        filename = path.split("/")[-1]  # 获取文件名，即 1314-1085.mp4
        basename = filename.split(".")[0]  # 去除扩展名，即 1314-1085
        # print(basename)
        basenameSuffix = filename.split(".")[1]  # 去除扩展名，即 1314-1085
        # print(basename)
        pathfinal = directory + "conversion_" + basename + "." + basenameSuffix
        minioClient.fput_object('oook', pathfinal, file)
    except ResponseError as err:
        print(err)

    # os.remove(file)
    return ReadConfigFile().read_config()[1] + pathfinal


def uploadDenoise(file, path, type):
    # 使用endpoint、access key和secret key来初始化minioClient对象。
    minioClient = Minio(ReadConfigFile().read_config()[0],
                        access_key=ReadConfigFile().read_config()[2],
                        secret_key=ReadConfigFile().read_config()[3],
                        secure=True)

    # 调用make_bucket来创建一个存储桶。
    filename = os.path.basename(file)
    miniopath = '/denoise/' + path + "/" + type + "/" + filename
    try:
        minioClient.fput_object('oook', miniopath, file)
    except ResponseError as err:
        print(err)

    # os.remove(file)
    return ReadConfigFile().read_config()[1] + miniopath


def uploadLiveRecord(file, miniopath):
    # 使用endpoint、access key和secret key来初始化minioClient对象。
    minioClient = Minio(ReadConfigFile().read_config()[0],
                        access_key=ReadConfigFile().read_config()[2],
                        secret_key=ReadConfigFile().read_config()[3],
                        secure=True)

    # 调用make_bucket来创建一个存储桶。
    # filename = os.path.basename(file)
    #  = '/data/mp4/' + filename
    try:
        minioClient.fput_object('oook', miniopath, file)
    except ResponseError as err:
        print(err)

    # os.remove(file)
    return miniopath


if __name__ == '__main__':
    # 当前目录
    # d = os.path.dirname(__file__)
    # abspath = os.path.abspath(d)
    # # final_url = 'https://minio.ambow.com/oook/1/%E5%9B%A0%E6%95%B8%E8%88%87%E9%99%AA%E6%95%B8-%E8%AA%AA%E6%95%B8%E8%A7%A3%E5%AD%97-%E6%8E%92.pptx'
    # final_url = 'https://minio.ambow.com/oook/1/%E5%9B%A0%E6%95%B8%E8%88%87%E9%99%AA%E6%95%B8-%E8%AA%AA%E6%95%B8%E8%A7%A3%E5%AD%97-%E6%8E%92.pdf'
    # # 测试用例
    #
    # r = upload(os.path.join(abspath, '53916-1111.webm'), 'abc', "pdf")
    # print(r)
    minioClient = Minio('minio.ambow.com',
                        access_key='dFVLI6LY7qwgrjvV',
                        secret_key='Rl3IyONdzse2IeOfixzv8FkC5PNB3HTB',
                        secure=True)

    # 调用make_bucket来创建一个存储桶。

    try:
        minioClient.copy_object(
            "oook",
            "1/2/3/4/500000516-7087.mp4",
            CopySource("oook", "/1/3/4/500000516-7087.mp4"))
    except ResponseError as err:
        print(err)
    # try:
    #     for version in minioClient.list_objects("oook","/test/特殊人群模板.xls"):
    #         print(version.object_name)
    #         print(version.version_id)
    #         # minioClient.remove_object(
    #         #     "my-bucket",
    #         #     version.object_name,
    #         #     version_id=version.version_id
    #         # )
    #     print("All object versions removed successfully")
    # except ResponseError as err:
    #     print(err)
    errors = minioClient.remove_object('oook',
                                       "/1/3/4/500000516-7087.mp4".encode('utf-8'))
    # for error in errors:
    #     print("error occurred when deleting object", error)
    # os.remove(file)
