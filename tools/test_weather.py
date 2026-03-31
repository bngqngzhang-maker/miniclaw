"""
天气查询工具 - 和风天气 API（带代理支持）
"""

import requests
import os


def search_weather(city: str) -> str:
    """
    查询天气
    """
    api_key = os.getenv("QWEATHER_API_KEY")
    
    if not api_key:
        return f"{city}|未配置API|--|--|--"
    
    # 代理配置（如果需要）
    proxies = {}
    http_proxy = os.getenv("http_proxy") or os.getenv("HTTP_PROXY")
    https_proxy = os.getenv("https_proxy") or os.getenv("HTTPS_PROXY")
    
    if http_proxy:
        proxies['http'] = http_proxy
    if https_proxy:
        proxies['https'] = https_proxy
    
    try:
        # 获取城市ID
        geo_resp = requests.get(
            "https://geoapi.qweather.com/v2/city/lookup",
            params={"location": city, "key": api_key},
            timeout=5,
            proxies=proxies if proxies else None
        )
        geo_data = geo_resp.json()
        
        if geo_data.get("code") != "200" or not geo_data.get("location"):
            return f"{city}|未找到城市|--|--|--"
        
        city_id = geo_data["location"][0]["id"]
        city_name = geo_data["location"][0]["name"]
        
        # 获取天气
        weather_resp = requests.get(
            "https://devapi.qweather.com/v7/weather/now",
            params={"location": city_id, "key": api_key},
            timeout=5,
            proxies=proxies if proxies else None
        )
        weather_data = weather_resp.json()
        
        if weather_data.get("code") != "200":
            return f"{city_name}|获取失败|--|--|--"
        
        now = weather_data["now"]
        
        return f"{city_name}|{now['text']}|{now['temp']}|{now['humidity']}|{now['windDir']}{now['windScale']}级"
        
    except requests.RequestException as e:
        return f"{city}|请求失败: {str(e)[:30]}|--|--|--"
    except Exception as e:
        return f"{city}|错误: {str(e)[:30]}|--|--|--"