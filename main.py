"""
什么值得买自动签到脚本
使用github actions 定时执行

优化版：
1. 增加签到状态判断
2. 推送内容更友好
3. 使用 getenv 防止环境变量不存在时报错

@author : stark
@modify : ChatGPT
"""

import os
import requests

import config
from utils.serverchan_push import push_to_wechat


class SMZDM_Bot(object):
    def __init__(self):
        self.session = requests.Session()
        self.session.headers = config.DEFAULT_HEADERS

    def __json_check(self, msg):
        """
        检查返回结果是否为 JSON
        """
        try:
            result = msg.json()
            print(result)
            return True
        except Exception as e:
            print(f'JSON解析失败: {e}')
            return False

    def load_cookie_str(self, cookies):
        """
        加载浏览器复制的 Cookie
        """
        self.session.headers['Cookie'] = cookies

    def checkin(self):
        """
        签到
        """
        url = 'https://zhiyou.smzdm.com/user/checkin/jsonp_checkin'

        try:
            msg = self.session.get(url, timeout=15)

            if self.__json_check(msg):
                return msg.json()

            return {
                "error_code": -1,
                "error_msg": "返回内容不是JSON"
            }

        except Exception as e:
            return {
                "error_code": -1,
                "error_msg": str(e)
            }


if __name__ == '__main__':

    cookies = os.getenv("COOKIES", "")
    server_key = os.getenv("SERVERCHAN_SECRETKEY", "")

    if not cookies:
        print("未配置 COOKIES")
        exit(1)

    bot = SMZDM_Bot()
    bot.load_cookie_str(cookies)

    print("开始签到...")
    res = bot.checkin()

    print("签到结果：")
    print(res)

    # 默认推送内容
    title = "什么值得买签到结果"
    desp = str(res)

    try:
        if res.get("error_code") == 0:

            data = res.get("data", {})

            point = data.get("point", 0)
            exp = data.get("exp", 0)
            gold = data.get("gold", 0)
            add_point = data.get("add_point", 0)
            continue_days = data.get("continue_checkin_days", 0)

            if add_point > 0:
                status = "🎉 今日签到成功"
            else:
                status = "✅ 今日已签到"

            desp = f"""
{status}

📅 连续签到：{continue_days} 天

⭐ 当前积分：{point}

💰 金币：{gold}

📖 经验：{exp}

➕ 本次获得积分：{add_point}
"""

        else:

            desp = f"""
❌ 签到失败

错误码：{res.get('error_code')}

错误信息：
{res.get('error_msg')}
"""

    except Exception as e:

        desp = f"""
⚠️ 数据解析异常

错误：
{e}

原始返回：
{res}
"""

    if server_key:

        print("检测到 Server酱 Key，开始推送...")

        try:
            push_to_wechat(
                text=title,
                desp=desp,
                secretKey=server_key
            )

            print("推送成功")

        except Exception as e:
            print("推送失败：", e)

    else:
        print("未配置 SERVERCHAN_SECRETKEY，跳过推送")

    print("代码执行完毕")
