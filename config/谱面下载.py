from urllib import request, error
import sys


def progressbar(cur, total=100):
    percent = '{:.2%}'.format(cur / total)
    sys.stdout.write('\r')
    # sys.stdout.write("[%-50s] %s" % ('=' * int(math.floor(cur * 50 / total)),percent))
    sys.stdout.write("[%-100s] %s" % ('=' * int(cur), percent))
    sys.stdout.flush()


def schedule(blocknum,blocksize,totalsize):
    """
    blocknum:当前已经下载的块
    blocksize:每次传输的块大小
    totalsize:网页文件总大小
    """
    if totalsize == 0:
        percent = 0
    else:
        percent = blocknum * blocksize / totalsize
    if percent > 1.0:
        percent = 1.0
    percent = percent * 100
    print("download : %.2f%%" %(percent))
    progressbar(percent)

url = "https://github.com/LibrarristShalinward/Deemo-I-Charts/raw/main/%E4%B8%8B%E8%BD%BD/%E4%BA%A4%E4%BA%92%E8%B0%B1%E9%9D%A2.zip"
path = r"./谱面/chart.zip"  # 文件下载后保存的本地路径
try:
    request.urlretrieve(url, path, schedule)
except error.HTTPError as e:
    print(e)
    print('\r\n' + url + ' download failed!' + '\r\n')
else:
    print('\r\n' + url + ' download successfully!')