from configparser import ConfigParser
import os

class ReadConfigFile(object):
    def read_config(self):
        conn = ConfigParser()
        file_path = os.path.join(os.path.abspath('.'), 'config.ini')
        if not os.path.exists(file_path):
            raise FileNotFoundError("文件不存在")

        conn.read(file_path)
        miniouploadurl = conn.get('api','miniouploadurl')
        miniourl = conn.get('api','miniourl')
        access_key = conn.get('api','access_key')
        secret_key = conn.get('api','secret_key')
        kafkaip = conn.get('api','kafkaip')


        return [miniouploadurl,miniourl,access_key,secret_key,kafkaip]

# rc = ReadConfigFile()
# print(ReadConfigFile().read_config()[0])