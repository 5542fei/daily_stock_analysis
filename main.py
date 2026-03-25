import akshare as ak
import pandas as pd
import datetime
import requests
import os

# ================= 配置区 =================
# 1. 在这里填入你关心的股票代码（纯数字）
MY_STOCKS = ['002092', '002702', '002624', '000721', '601007', '600121', '600313', '600690', '601988', '600900', '600019'] 

# ==========================================

def get_stock_prices():
    try:
        # 获取当前 A 股所有股票的实时/收盘行情（数据来源：东方财富）
        df = ak.stock_zh_a_spot_em()
        
        # 筛选出你关注的股票
        my_df = df[df['代码'].isin(MY_STOCKS)]
        
        today_str = datetime.datetime.now().strftime("%Y-%m-%d")
        msg_content = f"📅 {today_str} 收盘播报\n\n"
        
        # 遍历筛选结果并格式化输出
        for index, row in my_df.iterrows():
            name = row['名称']
            code = row['代码']
            price = row['最新价']
            pct_change = row['涨跌幅']
            
            # 根据涨跌幅添加个表情，好看一点
            emoji = "🔴" if pct_change > 0 else "🟢" if pct_change < 0 else "⚪"
            
            msg_content += f"{emoji} {name} ({code}): {price}元  (涨跌: {pct_change}%)\n"
            
        return msg_content
    except Exception as e:
        return f"获取股票数据失败: {e}"

def send_wechat_notification(content):
    # 使用 PushPlus (推送加) 发送到微信
    # 只要在 GitHub Secrets 中配置了 PUSHPLUS_TOKEN 就能发送
    token = os.environ.get('PUSHPLUS_TOKEN')
    if not token:
        print("未配置 PUSHPLUS_TOKEN，仅在控制台打印：")
        print(content)
        return

    url = 'http://www.pushplus.plus/send'
    data = {
        "token": token,
        "title": "📈 每日自选股收盘价",
        "content": content
    }
    response = requests.post(url, json=data)
    if response.status_code == 200:
        print("微信推送成功！")
    else:
        print(f"推送失败，状态码: {response.status_code}")

if __name__ == "__main__":
    # 1. 获取价格文本
    result_text = get_stock_prices()
    print(result_text) # 在 Action 日志中打印一份
    
    # 2. 发送推送到微信
    send_wechat_notification(result_text)
