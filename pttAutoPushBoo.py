#coding=utf-8
import telnetlib, sys, time, os, subprocess, re

###### CONSTANTS START ######
hostName = 'ptt.cc'
userId = ""
password = ""
boardName = 'test'
postId = '1DykZAQf'
inputFile = './text'
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
pushContentList = []
###### GLOBAL VAR END ######

def CheckLatency(hostName):
    global delayUnit
    print("Measuring host latency...")
    ping = subprocess.Popen(['ping', '-c', '10', hostName], stdout = subprocess.PIPE, stderr=subprocess.STDOUT)
    res, nothing = ping.communicate()
    res = re.match(".*([0-9]+)% .*\/([0-9.]+)\/[0-9.]+\/.*", res.decode('ascii'), flags = re.DOTALL)
    delayCoeff = 18
    if res.group(1) != '0':
        delayCoeff = 15
    delayUnit = float(res.group(2)) / delayCoeff
    print("Testing loss {0} %. Avg response time {1} ms.".format(res.group(1), res.group(2)))
    
def ReadSettings():
    global userId, password, boardName, postId, pushOption, inputFile
    print('Hello! I\'m PttAutoPushBoo!')
    userId = input('Please enter your user ID: ')
    password = input('Please enter your password: ')
    postId = input('Please enter the AID of the post you\'d like to push or boo\n(including the \'#\'): ')
    raw = re.match("#([A-Za-z0-9_]+)", postId)
    try:
        postId = raw.group(1)
    except:
        postId = postId
    boardName = input('Please enter the name of the board that the post belongs to: ')
    inputFile = input('Please enter the name of your input file: ')
    if not os.path.isfile(inputFile):
        if(not os.path.isfile('./text')):
        	Exit(6)
        print("OK, I'll use the default text file.")
        inputFile = './text'
    pushOption = input('What would you like to do? (1) push  (2) boo  (3) arrow  ')
    if pushOption > '3' or pushOption < '1':
        print('Invalid option! I\'ll boo anyway.')
        pushOption = 2
    print('Let\'s start!')

def Login(hostName, userId ,password) :
    global telnet
    telnet = telnetlib.Telnet(hostName)
    time.sleep(delayUnit)
    content = telnet.read_very_eager().decode('big5','ignore')
    if u"系統過載" in content :
        Exit(5)
        
    if u"請輸入代號" in content:
        #print ("輸入帳號中...")
        telnet.write((userId + "\r\n" ).encode('ascii'))
        time.sleep(delayUnit)
        #print ("輸入密碼中...")
        telnet.write((password + "\r\n").encode('ascii'))
        time.sleep(5 * delayUnit)
        content = telnet.read_very_eager().decode('big5','ignore')
        #print content
        if u"密碼不對" in content:
           Exit(4)
           #content = telnet.read_very_eager().decode('big5','ignore')
        if u"您想刪除其他重複登入" in content:
           print ('Removing other connections....')
           telnet.write(("y\r\n").encode('ascii'))
           time.sleep(15 * delayUnit)
           content = telnet.read_very_eager().decode('big5','ignore')
        if u"動畫播放中" in content:
           telnet.write(("\r\n" ).encode('ascii'))
           time.sleep(2 * delayUnit)
           content = telnet.read_very_eager().decode('big5','ignore')
        if u"請按任意鍵繼續" in content:
           #print ("資訊頁面，按任意鍵繼續...")
           telnet.write(("\r\n" ).encode('ascii'))
           time.sleep(2 * delayUnit)
           content = telnet.read_very_eager().decode('big5','ignore')
        if u"您要刪除以上錯誤嘗試" in content:
           print ("Erasing false attempts...")
           telnet.write(("y\r\n").encode('ascii'))
           time.sleep(5 * delayUnit)
           content = telnet.read_very_eager().decode('big5','ignore')
        if u"您有一篇文章尚未完成" in content:
           print ('Erasing undone posts....')
           # 放棄尚未編輯完的文章
           telnet.write(("q\r\n").encode('ascii'))
           time.sleep(5 * delayUnit)   
           content = telnet.read_very_eager().decode('big5','ignore')
        #print ("--- 登入完成 ---")
        
    else:
        Exit(7)

def Disconnect(error=False) :
    #if(not error):
    #    print ("登出中...")
    # q = 上一頁，直到回到首頁為止，g = 離開，再見
    telnet.write(("qqqqqqqqqg\r\ny\r\n" ).encode('ascii'))
    time.sleep(3 * delayUnit)
    #if(not error):
    #    print ("--- 登出完成 ---")
    telnet.close()

def Push(boardName, postId, pushType, pushContent):
    #print('--- 開始推文 ---')
    GoToBoard(boardName)
    #print('進入看板')
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
    #print('找到文章')

    # Shift-X
    telnet.write(('X').encode('ascii'))
    time.sleep(delayUnit)
    telnet.write(str(pushType).encode('ascii'))
    time.sleep(delayUnit)
    telnet.write((pushContent +'\r\n').encode('big5'))
    time.sleep(delayUnit)
    telnet.write(('y').encode('ascii'))
    time.sleep(delayUnit)
    #print ("--- 推文成功 ---")

def ReadPushContent(filename):
    global pushContentList
    file = open(filename, 'r')
    string = ""
    for line in file:
        if(line != '\n' and line != '\r\n'):
            string = string + line
    string = string.replace('\r\n', '')
    string = string.replace('\n', '')

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
            if byteLength + 2 > pushLength:
                pushContentList.append(substring)
                substring = string[i]
                byteLength = 2
            elif byteLength + 2 == pushLength:
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
    time.sleep(delayUnit)
    content = telnet.read_very_eager().decode('big5','ignore')
    pushLength = 0
    if u"推文時 不用對齊 開頭" in content:
        pushLength = maxIdLength - len(userId)
    if u"推文時 不會 記錄來源 IP" in content:
        pushLength = maxPushLength + pushLength
    else:
        pushLength = maxPushLengthWithIP + pushLength
    Disconnect()

def GoToBoard(boardName):
    # s 進入要發文的看板
    if not CheckBoardExists(boardName):
        Exit(1)
    telnet.write(('\r\n').encode('big5'))
    time.sleep(delayUnit)       
    telnet.write(("dd").encode('ascii'))   # in case of welcoming message
    time.sleep(2 * delayUnit)

def CheckBoardExists(boardName):
    telnet.write(('s').encode('ascii'))
    time.sleep(delayUnit)
    telnet.write(boardName.encode('big5'))
    time.sleep(2 * delayUnit)
    content = telnet.read_very_eager().decode('big5','ignore')
    if boardName in content:
        return True
    else:
        return False

def Exit(errorCode):
    print({
        1: "Cannot find this board.",
        2: "Cannot find this post.",
        3: "This post is removed.",
        4: "Wrong password or invalid account.",
        5: "The host is suffering heavy load. Try again later.",
        6: "Invalid Input File Name.",
        7: "The host may be offline now."
    }[errorCode])
    Disconnect()
    sys.exit(-1)

def main():

    ReadSettings()
    
    CheckLatency(hostName)
    start = time.time()
    print("Initializing...")
    CheckPushLength(boardName)
    ReadPushContent(inputFile)
    for i in range(len(pushContentList)):
        print("Now pushing: {0} / {1}".format(i + 1, len(pushContentList)), end='\r', flush=True)
        Login(hostName, userId ,password)    
        Push(boardName, postId, pushOption, pushContentList[i])
        Disconnect()
    print("Successfully pushed!")
    print("Total time: {0} sec.".format(time.time() - start))
	
if __name__=="__main__" :
    main()

