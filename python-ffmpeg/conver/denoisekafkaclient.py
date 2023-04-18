#!/bin/env python
import json

from kafka import KafkaConsumer
import audioDenoiseUbuntu
from ReadConfig import ReadConfigFile

# connect to Kafka server and pass the topic we want to consume
consumer = KafkaConsumer('denoise-live', group_id='ambow_getaway',
                         bootstrap_servers=[ReadConfigFile().read_config()[4]],
                         enable_auto_commit=False, auto_offset_reset='latest',
                         max_poll_interval_ms=1000*60*60*24)


def test():
    print(consumer.topics())
    print(consumer.subscription())
    try:
        for msg in consumer:
            try:
                consumer.commit()
            except:
                pass
            # print(msg)
            # print(msg.url)
            # print(msg.redirect_url)
            value = msg.value.decode('utf-8')
            #
            print(value)
            # js = json.dumps(value)
            # print("1:"+js)
            s1 = json.loads(value)
            # print('s1:' + s1)
            url = s1["url"]
            # print('url:' + url)
            redirect_url = s1["redirect_url"]
            # print('redirect_url:' + redirect_url)
            randomPath = s1["randomPath"]
            # print('randomPath:' + randomPath)
            audioDenoiseUbuntu.audioWavDenoise(url, redirect_url, randomPath)
            # print("%s:%d:%d: key=%s value=%s" % (msg.topic, msg.partition, msg.offset, msg.key, msg.value.decode('utf-8')))

    except Exception as e:
        print(e)


if __name__ == '__main__':
    # value='{"url": "https://minio.ambow.com/oook/1/%E5%9B%A0%E6%95%B8%E8%88%87%E9%99%AA%E6%95%B8-%E8%AA%AA%E6%95%B8%E8%A7%A3%E5%AD%97-%E6%8E%92.pptx", "redirect_url": "https://127.0.0.1:29000"}'
    # js = json.dumps(value)
    # s1 = json.loads(js)
    # print('s1:' + s1)
    # url = s1['url']
    # print('url:' + url)
    # expect_json = {"result": {"a": 1}}
    # expect_json_str = json.dumps(expect_json)
    # unexpect_json = {"result": "a"}
    # unexpect_json_str = json.dumps(unexpect_json)
    # unexpect_json_1 = {
    #     "url": "https://minio.ambow.com/oook/1/%E5%9B%A0%E6%95%B8%E8%88%87%E9%99%AA%E6%95%B8-%E8%AA%AA%E6%95%B8%E8%A7%A3%E5%AD%97-%E6%8E%92.pptx",
    #     "redirect_url": "https://127.0.0.1:29000"}
    # unexpect_json_str_1 = json.dumps(unexpect_json_1)
    # print(unexpect_json_str_1)
    # # key->"a"のvalue->1を参照
    # json_dict = json.loads(expect_json_str)
    # print(json_dict["result"])  # 1
    # print(json_dict["result"]["a"])  # 1
    #
    # # dictではないためエラー
    # json_dict = json.loads(unexpect_json_str)
    # print(json_dict["result"])
    # # print(json_dict["result"]["a"])
    # json_dict = json.loads(unexpect_json_str_1)
    # print(json_dict)
    # print(json_dict["url"])
    # print(json_dict["redirect_url"])
    test()
