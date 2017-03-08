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
import re


if len(sys.argv) != 8:  # 0 - имя испольняемого файла как аргумент
    print("""
    Неверное использование.
    Пример:
        upload.py host port encoding username password remotePATH filename
        """)
    sys.exit()

ftpHost = sys.argv[1]
ftpPort = sys.argv[2]
ftpEncoding = sys.argv[3]
ftpUsername = sys.argv[4]
ftpPassword = sys.argv[5]
ftpRemotePath = sys.argv[6].replace('я',u'яя')
ftpFilename = sys.argv[7]

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
ftpRemotePath = ftpRemotePath.replace('DD+1', '%02d' % int(dateInMSK.day + 1 + dayOffset))
ftpRemotePath = ftpRemotePath.replace('DD', '%02d' % int(dateInMSK.day + dayOffset))
ftpRemotePath = ftpRemotePath.split('/')
try:
    ftp = FTP()
    ftp.connect(host=ftpHost, port=int(ftpPort), timeout=5)
    ftp.login(user=ftpUsername, passwd=ftpPassword)
    ftp.encoding = ftpEncoding
except Exception as ex:
    print(ex)


for ftpRemotePathItem in ftpRemotePath:
    print('Текущий каталог: ' + ftp.pwd())
    changeDir = False
    try:
        lst=[]
        ftpdirlist=[]
        ftp.retrlines('LIST', lst.append)
        print(lst)
        for lstItem in lst:
            if re.match(r'^d.*', lstItem):
            #if lstItem.find('rwx') > 0:
                #ftpdirlist.append(re.sub(r'^.......................................................','', lstItem))
                ftpdirlist.append(lstItem)
                doublechar='я'
            else:
                #ftpdirlist.append(re.sub(r'^.........................................','', lstItem))
                ftpdirlist.append(lstItem)
                doublechar='яя'
        countitems = 1
        if len(ftpdirlist) == 0:
            print('Создаем директорию -> ' + ftpRemotePathItem)
            ftp.mkd(ftpRemotePathItem)         
            #ftp.cwd(ftp.nlst()[0])
            ftp.cwd(ftpRemotePathItem)
            continue
            
            
        for dirlistItem in ftpdirlist:
            #if ftpRemotePathItem == dirlistItem:
            if re.match(r'^.*' + ftpRemotePathItem + '$', dirlistItem):
                ftp.cwd(ftpRemotePathItem)
                changeDir = True
                break
            elif countitems == len(ftpdirlist):
                print('Создаем директорию -> ' + ftpRemotePathItem)
                ftp.mkd(ftpRemotePathItem)                
                ftp.cwd(ftpRemotePathItem)
                break
            else:                           
                countitems = countitems + 1
                continue  
    except Exception as ex:
        print(ex)
try:
    forSend = open(ftpFilename, 'rb')
    ftp.storbinary("STOR " + ftpFilename.replace('я',doublechar), forSend)
    forSend.close()
    ftp.quit()
except Exception as e:
    print(e)
