import subprocess
import threading
import platform


def run_script(script_name):
    if platform.system() != 'Windows':
        subprocess.run(['python3', script_name])
    else:
        subprocess.run(['python', script_name])


# 要启动的脚本列表
script_list = ['rote.py',
               'videoLiveRecordkafkaclient.py',
               'denoisekafkaclient.py',
               'videokafkaclient.py',
               # 'livekafkaclient.py',
               # 'kafkaclient.py',
               'livevideokafkaclient.py']

# 创建一个线程列表
threads = []
def start():
    # 启动每个脚本
    for script_name in script_list:
        thread = threading.Thread(target=run_script, args=(script_name,))
        thread.start()
        threads.append(thread)

    # 等待所有线程结束
    for thread in threads:
        thread.join()

if __name__ == '__main__':
    start()