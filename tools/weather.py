# """
# 天气查询工具 - 和风天气 API
# """

# import requests
# import os
# import logging

# logger = logging.getLogger(__name__)


# def search_weather(city: str) -> str:
#     """
#     查询天气
    
#     Args:
#         city: 城市名称
    
#     Returns:
#         格式: 城市|天气|温度|湿度|风力
#     """
#     api_key = os.getenv("QWEATHER_API_KEY")
    
#     if not api_key:
#         logger.warning("未配置 QWEATHER_API_KEY")
#         return f"{city}|未配置API|--|--|--"
    
#     try:
#         # 1. 获取城市ID
#         geo_resp = requests.get(
#             "https://geoapi.qweather.com/v2/city/lookup",
#             params={"location": city, "key": api_key},
#             timeout=5
#         )
#         geo_data = geo_resp.json()
        
#         # 调试信息
#         logger.debug(f"城市搜索响应: {geo_data}")
        
#         if geo_data.get("code") != "200":
#             logger.error(f"城市搜索失败: {geo_data}")
#             return f"{city}|未找到城市|--|--|--"
        
#         locations = geo_data.get("location", [])
#         if not locations:
#             logger.error(f"未找到城市: {city}")
#             return f"{city}|未找到城市|--|--|--"
        
#         # 取第一个匹配的城市
#         city_info = locations[0]
#         city_id = city_info["id"]
#         city_name = city_info["name"]
        
#         logger.debug(f"找到城市: {city_name}, ID: {city_id}")
        
#         # 2. 获取天气
#         weather_resp = requests.get(
#             "https://devapi.qweather.com/v7/weather/now",
#             params={"location": city_id, "key": api_key},
#             timeout=5
#         )
#         weather_data = weather_resp.json()
        
#         logger.debug(f"天气响应: {weather_data}")
        
#         if weather_data.get("code") != "200":
#             logger.error(f"获取天气失败: {weather_data}")
#             return f"{city_name}|获取失败|--|--|--"
        
#         now = weather_data.get("now", {})
#         if not now:
#             logger.error(f"天气数据为空: {weather_data}")
#             return f"{city_name}|无数据|--|--|--"
        
#         result = f"{city_name}|{now.get('text', '未知')}|{now.get('temp', '--')}|{now.get('humidity', '--')}|{now.get('windDir', '')}{now.get('windScale', '')}级"
#         logger.debug(f"天气结果: {result}")
        
#         return result
        
#     except requests.RequestException as e:
#         logger.error(f"网络请求失败: {e}")
#         return f"{city}|网络错误|--|--|--"
#     except Exception as e:
#         logger.error(f"未知错误: {e}")
#         return f"{city}|查询失败|--|--|--"
"""
天气查询工具 - 使用免费 API（无需 Key，支持预报）
"""

import requests
import json
from datetime import datetime, timedelta


def parse_date_keyword(date_keyword: str) -> int:
    """
    解析日期关键词，返回天数偏移
    
    Args:
        date_keyword: 日期关键词，如 "今天", "明天", "后天"
    
    Returns:
        天数偏移，0=今天，1=明天，2=后天
    """
    if not date_keyword:
        return 0
    
    date_map = {
        "今天": 0,
        "today": 0,
        "现在": 0,
        "当前": 0,
        "明天": 1,
        "tomorrow": 1,
        "后天": 2,
        "day after tomorrow": 2,
    }
    
    return date_map.get(date_keyword, 0)


def search_weather(city: str, date: str = None, day: str = None) -> str:
    """
    查询天气 - 使用 wttr.in 免费服务
    
    Args:
        city: 城市名称
        date: 日期（如 "明天", "后天"）
        day: 日期别名
    
    Returns:
        格式: 城市|天气|温度|湿度|风力
    """
    # 获取日期偏移
    query_date = date or day
    days_offset = parse_date_keyword(query_date) if query_date else 0
    
    try:
        if days_offset == 0:
            # 实时天气
            response = requests.get(
                f"https://wttr.in/{city}?format=%l|%C|%t|%h|%w",
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.text.strip()
                parts = result.split('|')
                if len(parts) >= 3:
                    # 清理温度格式，如 "+22°C" -> "22"
                    temp = parts[2].replace('+', '').replace('°C', '').replace('−', '-')
                    parts[2] = temp
                    result = '|'.join(parts)
                return result
            else:
                return f"{city}|服务不可用|--|--|--"
        
        else:
            # 预报天气 - 使用 wttr.in 的预报功能
            response = requests.get(
                f"https://wttr.in/{city}?format=j1",
                timeout=5
            )
            
            if response.status_code != 200:
                return f"{city}|预报服务不可用|--|--|--"
            
            data = response.json()
            
            # 获取预报数据
            weather_data = data.get("weather", [])
            if len(weather_data) <= days_offset:
                return f"{city}|预报数据不足|--|--|--"
            
            forecast = weather_data[days_offset]
            
            # 解析天气信息
            weather_desc = forecast.get("hourly", [{}])[0].get("weatherDesc", [{}])[0].get("value", "未知")
            temp_min = forecast.get("mintempC", "--")
            temp_max = forecast.get("maxtempC", "--")
            humidity = forecast.get("avghumidity", "--")
            wind_speed = forecast.get("avgspeedKmph", "--")
            
            # 计算星期几
            target_date = datetime.now() + timedelta(days=days_offset)
            weekday = ["一", "二", "三", "四", "五", "六", "日"][target_date.weekday()]
            
            return f"{city}|{weather_desc}|{temp_min}~{temp_max}|{humidity}|{wind_speed}km/h|星期{weekday}"
        
    except requests.exceptions.Timeout:
        return f"{city}|请求超时|--|--|--"
    except requests.exceptions.ConnectionError:
        return f"{city}|网络错误|--|--|--"
    except Exception as e:
        return f"{city}|错误:{str(e)[:20]}|--|--|--"