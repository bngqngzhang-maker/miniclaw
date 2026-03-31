"""
时间查询工具实现
"""

from datetime import datetime


def get_current_time() -> str:
    """
    获取当前时间
    
    Returns:
        格式化的时间字符串
    """
    now = datetime.now()
    weekdays = ["一", "二", "三", "四", "五", "六", "日"]
    weekday = weekdays[now.weekday()]
    
    return f"{now.year}|{now.month}|{now.day}|{now.hour}|{now.minute}|{now.second}|{weekday}"