import os
from xmlrpc.client import ResponseError

from minio import Minio

from ReadConfig import ReadConfigFile


def remove(myobject):
    # 使用endpoint、access key和secret key来初始化minioClient对象。
    minioClient = Minio('minio.ambow.com',
                        access_key='dFVLI6LY7qwgrjvV',
                        secret_key='Rl3IyONdzse2IeOfixzv8FkC5PNB3HTB',
                        secure=True)

    # 调用make_bucket来创建一个存储桶。
    try:
        minioClient.remove_objects('oook', myobject)
    except ResponseError as err:
        print(err)

    # os.remove(file)


def removeListFile(prefix="a"):
    minioClient = Minio(ReadConfigFile().read_config()[0],
                        access_key=ReadConfigFile().read_config()[2],
                        secret_key=ReadConfigFile().read_config()[3],
                        secure=True)

    # 调用make_bucket来创建一个存储桶。
    # try:
    #     # force evaluation of the remove_objects() call by iterating over
    #     # the returned value.
    #     minioClient.remove_object('oook', '/wps/X8uaqvznf8kT9SR4bkeJqw/png/10.png')
    # except ResponseError as err:
    #     print(err)
    #  因开启了版本控制.所以删除文件的同时不会删除空文件夹
    objects = minioClient.list_objects('oook', prefix='/wps/' + prefix,
                                       recursive=True)
    fileList = []
    for obj in objects:
        minioClient.remove_object('oook', obj.object_name.encode('utf-8'))
        print(obj.object_name)
        fileList.append(obj.object_name)
        print(obj.bucket_name, obj.object_name.encode('utf-8'), obj.last_modified,
              obj.etag, obj.size, obj.content_type)
    return fileList


if __name__ == '__main__':
    minioClient = Minio('minio.ambow.com',
                        access_key='dFVLI6LY7qwgrjvV',
                        secret_key='Rl3IyONdzse2IeOfixzv8FkC5PNB3HTB',
                        secure=True)

    # 调用make_bucket来创建一个存储桶。
    # try:
    #     # force evaluation of the remove_objects() call by iterating over
    #     # the returned value.
    #     minioClient.remove_object('oook', '/wps/X8uaqvznf8kT9SR4bkeJqw/png/10.png')
    # except ResponseError as err:
    #     print(err)

    objects = minioClient.list_objects('oook', prefix='/wps/' + "a",
                                       recursive=True)
    fileList = []
    for obj in objects:
        minioClient.remove_object('oook', obj.object_name.encode('utf-8'))
        print(obj.object_name)
        fileList.append(obj.object_name)
        print(obj.bucket_name, obj.object_name.encode('utf-8'), obj.last_modified,
              obj.etag, obj.size, obj.content_type)

    print(fileList)
