#coding=utf-8
import telnetlib
import sys
import time


host = 'ptt.cc'
user = sys.argv[1]
password = sys.argv[2]

# when longer internet delay, adjust this constant
delayUnit = 0.5

# max length of push message in character
lengthWithIP = 32
length = 48

def Login(host, user ,password) :
    global telnet
    telnet = telnetlib.Telnet(host)
    time.sleep(delayUnit)
    content = telnet.read_very_eager().decode('big5','ignore')
    if u"系統過載" in content :
        print("系統過載, 請稍後再來")
        sys.exit(0)
        

    if u"請輸入代號" in content:
        print ("輸入帳號中...")
        telnet.write((user + "\r\n" ).encode('ascii'))
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
           time.sleep(10 * delayUnit)
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

def disconnect(error=False) :
    if(not error):
        print ("登出中...")
    # q = 上一頁，直到回到首頁為止，g = 離開，再見
    telnet.write(("qqqqqqqqqg\r\ny\r\n" ).encode('ascii'))
    time.sleep(3 * delayUnit)
    #content = telnet.read_very_eager().decode('big5','ignore')
    #print content
    if(not error):
        print ("--- 登出完成 ---")
    telnet.close()

def Push(board, postId, pushType, pushContent):
    print('--- 開始推文 ---')
    # s 進入要發文的看板
    telnet.write(('s').encode('ascii'))
    telnet.write((board + '\r\n').encode('big5'))
    time.sleep(delayUnit)       
    telnet.write(("d").encode('ascii'))   # in case of welcoming message
    time.sleep(2 * delayUnit)
    print('進入看板')
    # go to post
    telnet.write(('#').encode('ascii'))
    time.sleep(delayUnit)
    telnet.write((postId + '\r\n').encode('ascii'))
    time.sleep(2 * delayUnit)

    content = telnet.read_very_eager().decode('big5','ignore')
    if u"找不到這個文章代碼" in content:
        telnet.write(("y\r\n").encode('ascii'))
        disconnect()
        raise Exception("找不到這個文章代碼!")
    elif u"本文已刪除" in content:
        telnet.write(("y\r\n").encode('ascii'))
        disconnect()
        raise Exception("本文已刪除!")
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


def main():
    for i in range(10):
        start = time.time()
        Login(host, user ,password)    
        Push('test', '1OVVlUja', 1, u'這是一篇測試,哇哈哈')
        disconnect()
        print(time.time() - start)
       

if __name__=="__main__" :
    main()

