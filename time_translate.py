# ** coding: utf-8 **
import time
import datetime

def time_to_now(t):
    '''
    Translate timestamp to how long ago. 
    '''
    res = ""
    cur_time = time.time()
    diff = cur_time - t
    if diff < 10:  # less than 10 seconds
        res = "刚刚"
    elif diff < 60:  # less than 1 min
        res = "{}秒前".format(str(int(diff)))
    elif diff < 60 * 60:  # less than 1 hour
        res = "{}分钟前".format(str(int(diff/60)))
    elif diff < 60 * 60 * 24:  # less than 1 day
        res = "{}小时前".format(str(int(diff/(60*60))))
    elif diff < 60 * 60 * 24 * 7:  # less than 1 week
        diff_days = int(diff/(60 * 60 * 24))
        if diff_days == 1:
            res = "昨天"
        elif diff_days == 2:
            res = "前天"
        else:
            res = "{}天前".format(str(diff_days))
    elif diff < 60 * 60 * 24 * 8:  # just larger than 1 week(8 days)
        res = "一周前"
    else:  # let it go
        day = datetime.date.fromtimestamp(t)
        res ="{year}年{month}月{day}日".format(
            year=str(day.year),
            month=str(day.month),
            day=str(day.day)
            )
    return res
