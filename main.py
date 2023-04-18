import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import time




def QA(data_face, data_lip, num):
    # 定义问题和选项
    question_1 = "Comparing the two full faces (Left and Right), which one looks more realistic?"
    options_1 = ["The Left one looks more realistic", "The Right one looks more realistic"]
    question_2 = "Comparing the lips of two faces, which one is more in sync with audio?"
    options_2 = ["The Left one is more in sync with audio", "The Right one is more in sync with audio"]

    # 显示问题并获取用户的答案
    answer_1 = st.radio(label=question_1, options=options_1, key=fr"button{num}.1")
    answer_2 = st.radio(label=question_2, options=options_2, key=fr"button{num}.2")

    # 以1/0数据保存
    ans1 = get_ans(answer_1)
    ans2 = get_ans(answer_2)

    # 保存结果到列表
    data_face[num - 1] = ans1
    data_lip[num - 1] = ans2

# 将用户的答案转化为1/0
def get_ans(answer_str):
    if "Left" in answer_str:
        return "1"
    elif "Right" in answer_str:
        return "0"

# 播放Video文件下的视频
def play_video(file_name):
    st.subheader(fr"Video")
    st.video(fr'merge_video/{file_name}',start_time=0)
    st.write("Please answer the following questions, after you watch the video. ")


def instrunction():
    st.subheader("Instructions: ")
    text1 = 'Please watch the four short videos (duration 4~7s) of two animated talking heads. \
            You need to choose the talking head (the left or the right) that moves more naturally in terms of the full face and the lips. '
    text2 = '**Reminder 1**: Please **turn on the sound on your computer** while you are watching the videos. '
    text3 = '**Reminder 2**: Some of the videos (one or two) are qualification testing videos.\
             **Your task might get rejected if you make the choices randomly**.'
    st.write(text1)
    st.write(text2)
    st.write(text3)


def data_collection(data_face, data_lip):
    # 发送内容
    data1 = ''.join(str(x) for x in data_face)
    data2 = ''.join(str(x) for x in data_lip)
    string = "face:" + data1 + "\n" + "lip:" + data2
    localtime = time.strftime('%Y-%m-%d %H-%M-%S', time.localtime())
    # 打开文件并指定写模式
    file_name = "data " + localtime + ".txt"
    file = open(file_name, "w")
    # 将字符串写入文件
    file.write(string)
    # 关闭文件
    file.close()
    # 发送邮件的账号和密码
    sender_email = "m15507509432@163.com"  # 发送者邮箱
    sender_password = "SGVSIFULLQWJGGZV"  # 发送者邮箱密码

    # 构建邮件主体
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = 'm15507509432@163.com'  # 收件人邮箱
    msg['Subject'] = 'data ' + localtime

    # 邮件正文
    text = MIMEText('')
    msg.attach(text)

    # 添加附件
    with open(file_name, 'rb') as f:
        attachment = MIMEApplication(f.read())
        attachment.add_header('Content-Disposition', 'attachment', filename=file_name)
        msg.attach(attachment)

    # 发送邮件
    try:
        smtp = smtplib.SMTP('smtp.163.com')
        smtp.login(sender_email, sender_password)
        smtp.sendmail(sender_email, ['m15507509432@163.com'], msg.as_string())
        smtp.quit()
        print('邮件发送成功')
    except smtplib.SMTPException as e:
        print('邮件发送失败，错误信息：', e)


def main():
    # 注意事项
    instrunction()
    file = open(r"file_list.txt", "r", encoding='utf-8') # 保证每次读取的文件顺序相同
    file_list = file.readlines()
    file.close()
    max_num = len(file_list)

    # 定义页面跳转函数，同时清空页面内容
    def switch_page(page_num):
        st.session_state["page_num"] = page_num
        st.session_state["data_face"] = data_face
        st.session_state["data_lip"] = data_lip
        st.experimental_rerun()  # 清空页面

    # 通过 st.session_state 实现页面跳转
    if "page_num" not in st.session_state:
        st.session_state["page_num"] = 1

    if "data_face" and "data_lip" not in st.session_state:
        # 初始化data变量
        data_face = [1 for x in range(0, max_num)]
        data_lip = [1 for x in range(0, max_num)]
    else:
        # 恢复data变量的状态
        data_face = st.session_state["data_face"]
        data_lip = st.session_state["data_lip"]

    num = st.session_state["page_num"]

    # 显示页面内容
    play_video(file_list[num].rstrip()) 
    QA(data_face, data_lip, num)

    # 显示上一页和下一页按钮
    # 第2页到31页
    if num > 1 and num < max_num:
        col1, col2 = st.columns(2)
        if col2.button("Previous"):
            switch_page(st.session_state["page_num"] - 1)
        if col1.button("Next"):
            switch_page(st.session_state["page_num"] + 1)

    # 第32页
    if st.session_state["page_num"] == max_num:
        col1, col2 = st.columns(2)
        if "button_clicked" not in st.session_state:
            st.session_state.button_clicked = False

        if not st.session_state.button_clicked:
            if col1.button("Submit results"):
                data_collection(data_face, data_lip)
                st.session_state.button_clicked = True

        if st.session_state.button_clicked == True:
            progress_bar = st.progress(0)  # 定义进度条，初始值为0
            for percent_complete in range(101):  # 逐渐增加进度条的值
                time.sleep(0.02)  # 休眠2秒以滴答声逐渐增加
                progress_bar.progress(percent_complete)  # 将当前的进度条值显示出来
            st.balloons()
            st.success("Successfully submitted the results. Thank you for using it. Now you can exit the system.")

        if col2.button("Previous"):
            switch_page(st.session_state["page_num"] - 1)

    # 第1页
    if st.session_state["page_num"] == 1:
        if st.button("Next"):
            switch_page(st.session_state["page_num"] + 1)


if __name__ == "__main__":
    main()
