#coding = utf-8
import requests
from datetime import datetime
import datetime
from dingtalkchatbot.chatbot import DingtalkChatbot
import time,json,re
from zhdate import ZhDate
from logging import *

#此可进行程序循环间隔执行的控制（单位是小时）
LOOP = 14 
PushTime = 10
#休息时间 推送时间

# 设置钉钉机器人的Webhook地址和Access Token
Ding_API=""
WX_API=""

DingWebHook='https://oapi.dingtalk.com/robot/send?access_token='
WxWebHook='https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=c'
dingtalk_bot = DingtalkChatbot(DingWebHook)

#企业微信机器人推送
def SendMsgToWechat(webhook=WxWebHook,msg=None):
    headers = {'Content-Type': 'application/json'}
    data = {
        "msgtype": "text",
        "text": {
            "content": msg,
            "mentioned_list":["@all"]
        }
    }
    r = requests.post(webhook, headers=headers, data=json.dumps(data))
    dict_r = json.loads(r.text)
    if (dict_r["errcode"] == 0) and (r.status_code == 200):
        push_print("+","企业微信机器人消息已经推送成功!")
    return 0

# 员工生日信息，格式为——>"姓名":"月-日"
# 1是公历，2是农历，0是输出全部员工信息
# 获取基本配置信息（员工生日信息和BOT开启状态）
# flag子类型的标志位，Flag=代表父类型  1,2目前为员工信息的子类型 
def read_file(flag=3,Flag="staff_info"):
    f = open('./birthday.json','r',encoding='utf-8')
    content = f.read()
    a = json.loads(content)
    # 机器人开启状态
    f2 = open('./config/config.json','r',encoding='utf-8')
    Bot_status = f2.read()
    b = json.loads(Bot_status)
    if(Flag=="staff_info"):
        #仔细看这个逻辑，这其实是循环两次去跑的农历和公历，并没去锁定
        for i,j in a.items():
            if (flag == '2') and (i == "农历"):
                a = j.items()
                return a
                #for m,n in j.items():
                    #print(m+"——"+n)
            elif (flag == '1') and (i == "公历"):
                a = j.items()
                return a
                #for m,n in j.items():
                    #print(m+"——"+n)
            elif flag == '0':#遍历输出所有员工信息
                #for i,j in a.items():
                print(i)
                num =0
                for n,m in j.items():
                    num+=1
                    print(num,"——",end="")
                    print(n+":",end="")
                    print(m)
                    #break
                print("——————————————————————————————————————————————————————")
            # else:
            #     push_print("-",f"函数read_file()flag参数有误,flag为{flag},i为{i},请联系管理员进行调试")
    elif(Flag=="bot"):
        return dict(b.items())
    else:
        push_print("-",f"read_file函数Flag参数有误,Flag为{Flag}请进行调整。")
        return 0
    
#农历与库中农历 同等格式
def moon_identify():
    now = ZhDate.today()
    pattern = re.compile(r'(?<=年).*')
    now_simple = str(now)
    a = pattern.search(now_simple)
    aa = a.group()
    b = str(aa).replace("月","-")
    c = str(b).replace("日","")
    return c

#格式化时间(小时分秒)输出
def format_time():
    current_time = time.localtime()
    formatted_time = time.strftime("%Y-%m-%d %H:%M:%S",current_time)
    return formatted_time

#内容输出格式化,作用于开发人员维护程序，可输入日志。
def push_print(flag='+',content=None):
    a = "[{flag}] [{time}] {content}".format(flag=flag,time=format_time(),content=content)
    print(a)

#输出阳历和阴历日期 1是公历 2是农历
def get_today(flag):
    sun = datetime.datetime.now().strftime("%Y年%m月%d日")
    moon = ZhDate.today()
    content = """
                今日阳历日期:{sun}
                今日阴历日期:{moon}""".format(sun=sun,moon=moon)
    if flag == 1:
        return sun
    elif flag == 2:
        return moon
    elif flag ==0:
        return content

#钉钉提醒语句 flag = 1是公历,2是农历
def send_message(name,days=None,birthday=None,flag=0):
    Bot_status = read_file(Flag="bot") 
    DDbot = Bot_status['DingBOT']
    WXbot = Bot_status['WechatBOT']
    if ((DDbot== '0')and(WXbot)=='0'):
        push_print(content="机器人推送已关闭，请联系管理员(lu_ferine@163.com)解决！")
        return 0
    if flag == '2':
        flag ="农历"
        message = f"主人，咱们亲爱的{name}，还有{days}天就要过生日啦！{name}的生日是{flag}{birthday}。请确认具体日期。祝{name}生日快乐！"
        if (DDbot == '1'):
            dingtalk_bot.send_text(msg=message, is_at_all=False)
        if WXbot== '1':
            SendMsgToWechat(msg=message)

    elif flag == '1':
        flag = "公历"
        message = f"主人，咱们亲爱的{name}，还有{days}天就要过生日啦！{name}的生日是{flag}{birthday}。请确认具体日期。祝{name}生日快乐！"
        if DDbot == '1':
            dingtalk_bot.send_text(msg=message, is_at_all=False)
        if WXbot== '1':
            SendMsgToWechat(msg=message)

    elif flag == 0:#维护消息
        message = f"{name}"
        if DDbot == '1':
            dingtalk_bot.send_text(msg=message, is_at_all=False,at_dingtalk_ids="15f-4pmz32fuaw")
        if WXbot== '1':
            SendMsgToWechat(msg=message)

#计算天数之差  flag = 1是公历,2是农历
def day_difference(flag):
    if flag == '1':#公历
        d1 = datetime.datetime.now().strftime("%m-%d")
        date1 = datetime.datetime.strptime(d1,"%m-%d").date()
        a = ["ID","姓名","生日相差天数","生日日期"]
        id = 0
        for m,n in read_file(flag,Flag="staff_info"):
            #print("唉")
            date2 = datetime.datetime.strptime(n,"%m-%d").date()
            Days = (date2-date1).days
            a.append(id)
            a.append(m)
            a.append(Days)
            a.append(n)
            id+=1
            #print(m,Days,n)
        return (a,id)
            
    elif flag == '2':#农历
        d1 = moon_identify()
        date3 = datetime.datetime.strptime(d1,"%m-%d").date()
        a = ["ID","姓名","生日相差天数","生日日期"]
        id = 0
        for m,n in read_file(flag):
            date4 = datetime.datetime.strptime(n,"%m-%d").date()
            Dayss = (date4-date3).days
            a.append(id)
            a.append(m)
            a.append(Dayss)
            a.append(n)                                                      
            id+=1
        return (a,id)
    
        #d2 = read_file(2)
    
#1是公历 2是农历
def main(flag):
    a = day_difference(flag)
    # 取返回列表中的ID，ID为7

    for x in range(1,a[1]+1):               #     [(7-3)*{1~6}+1]  #取列表中的姓名
        push_print("+",f"检查员工生日:{a[0][(4*x+1)]}")
               #生日相差天数>0 则再输出差几天，（也就是仅输出今年）近10天内的都输出。
        if a[0][(4*x+2)] > 0 and (a[0][(4*x+2)] < PushTime):                                                                                      #他的生日是
            push_print("+",f"发送提醒给:{a[0][(4*x+1)]}还有{a[0][(4*x+2)]}天就要过生日啦!,{a[0][(4*x+1)]}的生日是{a[0][(4*x+3)]}")
            send_message(a[0][(4*x+1)],a[0][(4*x+2)],a[0][(4*x+3)],flag)
            push_print("+","钉钉机器人消息已推送成功!")
            #break
        elif a[0][(4*x+2)]< 0:  #小于0的代表不在今年（农历，公历）
            push_print("-",f"{a[0][(4*x+1)]}的生日在明年!")
        elif a[0][(4*x+2)]> 0:
            push_print("-",f"{a[0][(4*x+1)]}的生日还有{a[0][(4*x+2)]}天。")
        else:
            push_print("-",f"{a[0][(4*x+1)]}的生日不在{PushTime}天内，暂不推送。")

# 获取版本信息
def read_versionINFO():
    f = open("./version/info.txt","r",encoding="utf-8")
    info = f.read()
    return info

# 监测版本更新输出到机器人API（打算后续实现在线升级和更新）
def Version_Update():
    return 0

#模块检查，检查各个模块是否工作正常，输出到控制台
def ModuleCheck():
    return 0

#LOGO
def Brand():
    return 0

#控制台控制输出
def GIFAConsole():
    f = open("./version/V0.5/console.txt","r",encoding="utf-8")
    info = f.read()
    push_print("+","您已经进入姬发程序管理控制台(半小时后将退出控制台),可输入对应键值进行如下操作!")
    return info

if __name__ == '__main__':

    #info = "姬发已经启动(目前为内测版v0.5),很多功能还在测试当中,预计下个版本加入日志记录功能,机器人推送支持MarkDown格式和人员入职周年推送等功能。另外各位有其他好的成熟的想法请联系我Email:lu_ferine@163.com。感谢使用!"
    #push_print("+",info)
    #send_message(name=info,days=None,birthday=None,flag=0)
    

    BotStatus = read_file(Flag="bot")
    Keep_running = True
    while Keep_running:
        print(GIFAConsole())
        Key = input("|----请按任意键启动姬发或输入STOP退出程序----:").upper()
        if (Key =="STOP") or (Key == "S"):
            Keep_running = False
            break
        elif (Key == "A"):
            read_file(str(0))
       	    continue
        elif (Key == "B"):
            push_print("+",f"机器人开启状态:{BotStatus}")
            continue
        elif (Key == "X"):
       	    push_print("公历生日倒计时信息",day_difference('1'))
            continue 
        elif (Key == "Y"):
            push_print("农历生日倒计时信息",day_difference('1'))
            continue   
        elif (Key == "Z"):
       	    push_print("版本更新信息",read_versionINFO())
            continue
        else:
            push_print("+",f"接受到命令:{Key}")

        if int(time.strftime("%H")) > 9 and int(time.strftime("%H")) < 23 and int((time.strftime("%w")))!=0:
            push_print("+","当前是工作时间")
            if Version_Update == 1:
                send_message(name=None,days=None,birthday=None,flag=0)
            print("|——————————————————————————————————————————————————|")
            push_print("+","现在检查公历的生日。")
            print("|++++++++++++++++++++++++++++++++++++++++++++++++++|")
            main('1')
            print("|——————————————————————————————————————————————————|")
            push_print("+","现在检查农历的生日。")
            print("|++++++++++++++++++++++++++++++++++++++++++++++++++|")
            time.sleep(3)
            main('2')
            #time.sleep(3)
            time.sleep(3600*LOOP)
        else:
            push_print("+","休息吧，社畜")
            time.sleep(5400) #一个半小时
    push_print("-","程序已退出。")
    '''    
    '''
