import datetime
import locale

# 设置中文本地化
try:
    locale.setlocale(locale.LC_TIME, 'zh_CN.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_TIME, 'Chinese_China.936')
    except:
        pass

now = datetime.datetime.now()

# 中文格式输出
print("当前时间：{}年{}月{}日 星期{} {}:{}:{}".format(
    now.year,
    now.month,
    now.day,
    ['一', '二', '三', '四', '五', '六', '日'][now.weekday()],
    str(now.hour).zfill(2),
    str(now.minute).zfill(2),
    str(now.second).zfill(2)
))
