# -*- coding: utf-8 -*-

"""
Created on 25 февр. 2017 г.

    Скрипт отправки данных на FTP сервер, все значения
    принимает через параметы командной строки.
    Важно - при отправке файла необходимо находиться в текущем каталоге.

    пример:
    python35 upload.py host port encoding username password remotePATH split_day_and_nigth filename
            host - "1.2.3.4" - адрес FTP сервера
            port - 21 - порт подключения
            encoding - "cp1251" - используемая на сервере кодировка
            username - "user" - имя пользователя
            password - "PasswdForUser" - пароль
            remotePATH - "destination/folder/YYYY/MM/DD/end/folder" - путь от корня (первый и последний сеши не пишем)
            split_day_and_nigth - "1" - разделять день и ночь (добавлять в конечный каталог папку с именем предыдущего дня)
            filename - "test.file" - файл с полным путем

@author: lakoriss
"""

from ftplib import FTP
from datetime import datetime, timedelta
import sys
import re


if len(sys.argv) != 9:  # 0 - имя испольняемого файла как аргумент
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
ftpSplitDayAndNight = int(sys.argv[7])
ftpFilename = sys.argv[8]

monthNames = ['ЯНВАРЬ', 'ФЕВРАЛЬ', 'МАРТ', 'АПРЕЛЬ', 'МАЙ', 'ИЮНЬ',
              'ИЮЛЬ', 'АВГУСТ', 'СЕНТЯБРЬ', 'ОКТЯБРЬ', 'НОЯБРЬ', 'ДЕКАБРЬ']


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
if dayOffset == 1 and ftpSplitDayAndNight == 1:
    ftpRemotePath.append(str(dateInMSK.day - dayOffset))
    
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
        # >>> bytes('ыыы', 'utf-8')
        # b'\xd1\x8b\xd1\x8b\xd1\x8b'
        # >>> b=bytes('ыыы', 'utf-8')
        # >>> b.decode()
        # 'ыыы'
        
        lst=ftp.mlsd('/')
        print(lst[0].decode())
        #ftp.retrlines('LIST', lst.append)
        ftp.retrbinary('LIST', lst.append) # возможно решение в бинарной структуре данных
        lst = bytes(lst[0], encoding='UTF-8').split("\r\n")
        # надо распарсить строку
        for lstItem in lst:
            print (lstItem.encode('utf-8'))
            if re.match(r'^d.*', lstItem):
                ftpdirlist.append(re.sub(r'^d.*[0-9]\ ','', lstItem))
                doublechar='я'
            elif re.match(r'.*\<DIR\>.*', lstItem):            
                ftpdirlist.append(re.sub(r'^.*<DIR>..........','', lstItem))
                doublechar='яя'
            else:
                continue
        countitems = 1
        if len(ftpdirlist) == 0:
            print('Создаем директорию -> ' + ftpRemotePathItem)
            ftp.mkd(ftpRemotePathItem)
            ftp.cwd(ftpRemotePathItem)
            continue
            
            
        for dirlistItem in ftpdirlist:
            if ftpRemotePathItem == dirlistItem:
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
    print("STORE...")
    # ftp.storbinary("STOR " + ftpFilename.replace('я',doublechar), forSend)
    forSend.close()
    ftp.quit()
except Exception as e:
    print(e)
