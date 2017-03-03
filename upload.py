# -*- coding: utf-8 -*-

"""
Created on 25 февр. 2017 г.

    Скрипт отправки данных на FTP сервер, все значения
    принимает через параметы командной строки.
    Важно - при отправке файла необходимо находиться в текущем каталоге.

    пример:
    python35 upload.py host port username password remotePATH filename

@author: lakoriss
"""

from ftplib import FTP
from datetime import datetime, timedelta
import sys


if len(sys.argv) != 7:  # 0 - имя испольняемого файла как аргумент
    print("""
    Неверное использование.
    Пример:
        upload.py host port username password remotePATH filename
        """)
    sys.exit()

ftpHost = sys.argv[1]
ftpPort = sys.argv[2]
ftpUsername = sys.argv[3]
ftpPassword = sys.argv[4]
ftpRemotePath = sys.argv[5].replace('я',"Я")
ftpFilename = sys.argv[6].replace('я',"Я")

monthNames = ['ЯНВАРЬ', 'ФЕВРАЛЬ', 'МАРТ', 'АПРЕЛЬ', 'МАЙ', 'ИЮНЬ',
              'ИЮЛЬ', 'АВГУСТ', 'СЕНТЯБРЬ', 'ОКТЯБРЬ', 'НОЯБРЬ', 'ДЕКАБРЬ']

# /YYYY/MM MONTH/DAY/

dateInMSK = datetime.utcnow() + timedelta(hours=3)
dayOffset=0
if dateInMSK.hour > 13:
    dayOffset=1
ftpRemotePath = ftpRemotePath.replace('YYYY', '%d' % dateInMSK.year)
ftpRemotePath = ftpRemotePath.replace('MM', '%02d' % dateInMSK.month)
ftpRemotePath = ftpRemotePath.replace('MONTH', '%s' % monthNames[int(dateInMSK.month - 1)])
ftpRemotePath = ftpRemotePath.replace('DD+1', '%d' % int(dateInMSK.day + 1 + dayOffset))
ftpRemotePath = ftpRemotePath.replace('DD', '%d' % int(dateInMSK.day + dayOffset))
ftpRemotePath = ftpRemotePath.split('/')
ftp = FTP()
ftp.connect(host=ftpHost, port=int(ftpPort), timeout=5)
ftp.login(user=ftpUsername, passwd=ftpPassword)
ftp.encoding = 'cp1251'

for ftpRemotePathItem in ftpRemotePath:
    # print(ftpDirName.encode())
    try:
        ftpdirlist = ftp.nlst()
        countitems = 1
        if len(ftpdirlist) == 0:
            print('Создаем директорию -> ' + ftpRemotePathItem)
            ftp.mkd(ftpRemotePathItem)         
            ftp.cwd(ftp.nlst()[0])
            print(ftp.pwd())
            continue
            
            
        for dirlistItem in ftpdirlist:
            if ftpRemotePathItem == dirlistItem:
                ftp.cwd(dirlistItem)
                print(ftp.pwd())
                break
            elif countitems == len(ftpdirlist):
                print('Создаем директорию -> ' + ftpRemotePathItem)
                ftp.mkd(ftpRemotePathItem)                
                ftp.cwd(ftpRemotePathItem)
                print(ftp.pwd())                
                break
            else:                           
                countitems = countitems + 1
                continue
            
    
      
    except Exception as ex:
        print(ex)

try:
    print(ftp.pwd())
    forSend = open(ftpFilename, 'rb')
    ftp.storbinary("STOR " + ftpFilename, forSend)
    forSend.close()
    ftp.quit()
except Exception as e:
    print(e)
    