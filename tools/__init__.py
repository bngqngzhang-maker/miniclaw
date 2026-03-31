"""
工具注册表
"""

from typing import Dict, Callable


class ToolRegistry:
    """工具注册表"""
    
    def __init__(self):
        self._tools: Dict[str, Callable] = {}
        self._register()
    
    def _register(self):
        """注册所有工具"""
        from .weather import search_weather
        from .web_search import web_search
        from .timer import create_timer_task
        from .time_tool import get_current_time
        
        self._tools["search_weather"] = search_weather
        self._tools["web_search"] = web_search
        self._tools["create_timer_task"] = create_timer_task
        self._tools["get_current_time"] = get_current_time
    
    def get(self, name: str) -> Callable:
        """获取工具"""
        return self._tools.get(name)
    
    def get_tools_description(self) -> list:
        """获取工具描述"""
        return [
            {
                "name": "search_weather",
                "description": "查询城市天气，返回天气、温度、湿度、风力等信息",
                "args": {"city": "城市名称，如'北京'、'上海'"}
            },
            {
                "name": "web_search",
                "description": "搜索网络信息",
                "args": {"query": "搜索关键词"}
            },
            {
                "name": "create_timer_task",
                "description": "创建定时任务，在指定时间后提醒用户",
                "args": {"delay_seconds": "延迟秒数", "message": "提醒内容"}
            },
            {
                "name": "get_current_time",
                "description": "获取当前时间",
                "args": {}
            },
        ]