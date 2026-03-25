import akshare as ak
import pandas as pd
import datetime
import os
import smtplib
from email.mime.text import MIMEText
from email.header import Header

# ================= 配置区 =================
# 1. 在这里填入你关心的股票代码（纯数字）
MY_STOCKS = ['002092', '002702', '002624', '000721', '601007', '600121', '600313', '600690', '601988', '600900', '600019'] 

# ==========================================

def get_stock_prices():
    try:
        # 获取当前 A 股所有股票的实时/收盘行情
        df = ak.stock_zh_a_spot_em()
        
        # 筛选出你关注的股票
        my_df = df[df['代码'].isin(MY_STOCKS)]
        
        today_str = datetime.datetime.now().strftime("%Y-%m-%d")
        msg_content = f"📅 {today_str} 收盘播报\n\n"
        
        for index, row in my_df.iterrows():
            name = row['名称']
            code = row['代码']
            price = row['最新价']
            pct_change = row['涨跌幅']
            
            # 根据涨跌幅添加个表情
            emoji = "🔴" if pct_change > 0 else "🟢" if pct_change < 0 else "⚪"
            
            msg_content += f"{emoji} {name} ({code}): {price}元  (涨跌: {pct_change}%)\n"
            
        return msg_content
    except Exception as e:
        return f"获取股票数据失败: {e}"

def send_email(content):
    # 从 GitHub Secrets 中读取邮箱配置
    sender = os.environ.get('EMAIL_SENDER')     # 发件人邮箱，如 xxx@163.com
    password = os.environ.get('EMAIL_PASS')     # 163邮箱的授权码（不是登录密码）
    receiver = os.environ.get('EMAIL_RECEIVER') # 收件人邮箱（可以是同一个163邮箱，也可以是其他邮箱）

    if not all([sender, password, receiver]):
        print("未检测到完整的邮箱配置，仅在控制台打印：")
        print(content)
        return

    # 配置网易 163 的 SMTP 服务器
    smtp_server = "smtp.163.com"
    smtp_port = 465  # 163邮箱 SSL 加密端口
    
    # 构造邮件正文
    message = MIMEText(content, 'plain', 'utf-8')
    message['From'] = Header("自选股机器人", 'utf-8')
    message['To'] = Header("主人", 'utf-8')
    
    today_str = datetime.datetime.now().strftime("%m月%d日")
    message['Subject'] = Header(f"📈 {today_str} 自选股收盘播报", 'utf-8')

    try:
        # 使用 SSL 加密连接
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        server.login(sender, password)
        server.sendmail(sender, [receiver], message.as_string())
        server.quit()
        print("邮件发送成功！请查收。")
    except smtplib.SMTPException as e:
        print(f"邮件发送失败: {e}")

if __name__ == "__main__":
    # 1. 获取价格文本
    result_text = get_stock_prices()
    print(result_text) # 打印到 Action 日志备查
    
    # 2. 发送邮件
    send_email(result_text)
