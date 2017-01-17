#coding=utf-8
import telnetlib, sys, time, os, subprocess, re

###### CONSTANTS START ######
hostName = 'ptt.cc'
userId = sys.argv[1]
password = sys.argv[2]
boardName = 'test'
postId = '1DykZAQf'
pushOption = 2

# max length of push message in character
maxPushLengthWithIP = 32
maxPushLength = 48

maxIdLength = 12
####### CONSTANTS END #######

###### GLOBAL VAR START ######
# when longer internet delay, adjust this variable manually
delayUnit = 0.5
pushLength = 48
pushContentList = [];
###### GLOBAL VAR END ######

def CheckLatency(hostName):
    global delayUnit
    print("Measuring host latency...")
    ping = subprocess.Popen(['ping', '-c', '10', hostName], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    res, nothing = ping.communicate()
    res = re.match(".*([0-9]+)% .*\/([0-9.]+)\/[0-9.]+\/.*", res.decode('ascii'), flags=re.DOTALL)
    delayUnit = float(res.group(2)) / 15
    print("Testing loss", res.group(1), "%. Avg response time", float(res.group(2)), "ms.") 
    

def Login(hostName, userId ,password) :
    global telnet
    telnet = telnetlib.Telnet(hostName)
    time.sleep(delayUnit)
    content = telnet.read_very_eager().decode('big5','ignore')
    if u"系統過載" in content :
        print("系統過載, 請稍後再來")
        sys.exit(0)
        

    if u"請輸入代號" in content:
        print ("輸入帳號中...")
        telnet.write((userId + "\r\n" ).encode('ascii'))
        time.sleep(delayUnit)
        print ("輸入密碼中...")
        telnet.write((password + "\r\n").encode('ascii'))
        time.sleep(5 * delayUnit)
        content = telnet.read_very_eager().decode('big5','ignore')
        #print content
        if u"密碼不對" in content:
           print("密碼不對或無此帳號。程式結束")
           sys.exit()
           content = telnet.read_very_eager().decode('big5','ignore')
        if u"您想刪除其他重複登入" in content:
           print ('刪除其他重複登入的連線....')
           telnet.write(("y\r\n").encode('ascii'))
           time.sleep(15 * delayUnit)
           content = telnet.read_very_eager().decode('big5','ignore')
        if u"請按任意鍵繼續" in content:
           print ("資訊頁面，按任意鍵繼續...")
           telnet.write(("\r\n" ).encode('ascii'))
           time.sleep(2 * delayUnit)
           content = telnet.read_very_eager().decode('big5','ignore')
        if u"您要刪除以上錯誤嘗試" in content:
           print ("刪除以上錯誤嘗試...")
           telnet.write(("y\r\n").encode('ascii'))
           time.sleep(5 * delayUnit)
           content = telnet.read_very_eager().decode('big5','ignore')
        if u"您有一篇文章尚未完成" in content:
           print ('刪除尚未完成的文章....')
           # 放棄尚未編輯完的文章
           telnet.write(("q\r\n").encode('ascii'))
           time.sleep(5 * delayUnit)   
           content = telnet.read_very_eager().decode('big5','ignore')
        print ("--- 登入完成 ---")
        
    else:
        print ("沒有可輸入帳號的欄位，網站可能掛了")

def Disconnect(error=False) :
    if(not error):
        print ("登出中...")
    # q = 上一頁，直到回到首頁為止，g = 離開，再見
    telnet.write(("qqqqqqqqqg\r\ny\r\n" ).encode('ascii'))
    time.sleep(5 * delayUnit)
    if(not error):
        print ("--- 登出完成 ---")
    telnet.close()

def Push(boardName, postId, pushType, pushContent):
    print('--- 開始推文 ---')
    GoToBoard(boardName)
    print('進入看板')
    # go to post
    telnet.write(('#').encode('ascii'))
    time.sleep(delayUnit)
    telnet.write((postId + '\r\n').encode('ascii'))
    time.sleep(delayUnit)

    content = telnet.read_very_eager().decode('big5','ignore')
    if u"找不到這個文章代碼" in content:
        Exit(2)
    elif u"本文已刪除" in content:
        Exit(3)
    print('找到文章')

    # Shift-X
    telnet.write(('X').encode('ascii'))
    time.sleep(delayUnit)
    telnet.write(str(pushType).encode('ascii'))
    time.sleep(delayUnit)
    telnet.write((pushContent +'\r\n').encode('big5'))
    time.sleep(delayUnit)
    telnet.write(('y').encode('ascii'))
    time.sleep(delayUnit)
    print ("--- 推文成功 ---")

def ReadPushContent(filename):
    global pushContentList
    file = open(filename, 'r')
    string = ""
    for line in file:
        if(line != '\n' and line != '\r\n'):
            string = string + line
    string = string.replace('\n', '')
    string = string.replace('\r\n', '')

    substring = ""
    substringEng = ""
    byteLength = 0
    inHalf = False
    for i in range(len(string)):
        if IsFullWidthCharacter(string[i]):
            if inHalf:               # half width word ended
                inHalf = False       # Check if necessary to start a new line
                if (byteLength + len(substringEng) > pushLength):
                    pushContentList.append(substring)
                    substring = substringEng
                    byteLength = len(substringEng)
                elif (byteLength + len(substringEng) == pushLength):
                    substring = substring + substringEng
                    byteLength = 0
                    pushContentList.append(substring)
                    substring = ""
                else:
                    byteLength = byteLength + len(substringEng)
                    substring = substring + substringEng
                substringEng = ""
            if (byteLength + 2 > pushLength):
                pushContentList.append(substring)
                substring = string[i]
                byteLength = 2
            elif(byteLength + 2 == pushLength):
                substring = substring + string[i]
                pushContentList.append(substring)
                byteLength = 0
                substring = ""
            else:
                substring = substring + string[i]
                byteLength = byteLength + 2

        else:
            if(not inHalf):
                inHalf = True
            substringEng = substringEng + string[i]
    pushContentList.append(substring)

def IsFullWidthCharacter(char):
    if ((char >= u'\u4E00' and char <= u'\u9FCC')         # CJK
        or (char >= u'\u3400' and char <= u'\u4DB5')
        or (char >= u'\u20000' and char <= u'\u2A6D6')
        or (char >= u'\u2A700' and char <= u'\u2B734')
        or (char >= u'\u2B740' and char <= u'\u2B81D')
        or (char >= u'\u3000' and char <= u'\u303F')      # CJK punctuation
        or (char >= u'\uFF00' and char <= u'\uFF60')      # full width ascii
        or (char >= u'\uFFE0' and char <= u'\uFFE6')
    ):
        return True
    else:
        return False

def CheckPushLength(boardName):
    global pushLength
    Login(hostName, userId ,password)
    GoToBoard(boardName)
        # check board settings
    telnet.write(('i').encode('ascii'))
    content = telnet.read_very_eager().decode('big5','ignore')
    pushLength = 0
    if u"推文時 不用對齊 開頭" in content:
        pushLength = maxIdLength - len(userId)
    if u"推文時 不會 記錄來源 IP" in content:
        pushLength = maxPushLength + pushLength
    else:
        pushLength = maxPushLengthWithIP + pushLength
    telnet.write(('i').encode('ascii'))
    Disconnect()

def GoToBoard(boardName):
    # s 進入要發文的看板
    if(not CheckBoardExists(boardName)):
        Exit(1)
    telnet.write(('\r\n').encode('big5'))
    time.sleep(delayUnit)       
    telnet.write(("d").encode('ascii'))   # in case of welcoming message
    time.sleep(2 * delayUnit)

def CheckBoardExists(boardName):
    telnet.write(('s').encode('ascii'))
    telnet.write(boardName.encode('big5'))
    time.sleep(delayUnit)
    content = telnet.read_very_eager().decode('big5','ignore')
    if(boardName in content):
        return True
    else:
        return False

def Exit(errorCode):
    print({
        1: "找不到這個看板!",
        2: "找不到這個文章代碼!",
        3: "本文已刪除!"
    }[errorCode])
    Disconnect()
    sys.exit(-1)

def main():
    print("Start Pushing...")
    start = time.time()
    CheckLatency(hostName)
    CheckPushLength(boardName)
    ReadPushContent('./text')
    for i in range(len(pushContentList)):
        Login(hostName, userId ,password)    
        Push(boardName, postId, pushOption, pushContentList[i])
        Disconnect()
    print("Total time:", time.time() - start)
    
if __name__=="__main__" :
    main()

