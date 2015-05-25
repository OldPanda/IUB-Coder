# ** coding: utf-8 **
import time
import datetime

def time_to_now(t):
    res = ""
    cur_time = time.time()
    diff = cur_time - t
    if diff < 10:
        res = "刚刚"
    elif diff < 60:
        res = "{}秒前".format(str(int(diff)))
    elif diff < 60 * 60:
        res = "{}分钟前".format(str(int(diff/60)))
    elif diff < 60 * 60 * 24:
        res = "{}小时前".format(str(int(diff/(60*60))))
    elif diff < 60 * 60 * 24 * 7:
        diff_days = int(diff/(60 * 60 * 24))
        if diff_days == 1:
            res = "昨天"
        elif diff_days == 2:
            res = "前天"
        else:
            res = "{}天前".format(str(diff_days))
    elif diff < 60 * 60 * 24 * 8:
        res = "一周前"
    else:
        day = datetime.date.fromtimestamp(t)
        res ="{year}年{month}月{day}日".format(
            year=str(day.year),
            month=str(day.month),
            day=str(day.day)
            )
    return res
