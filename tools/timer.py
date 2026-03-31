"""
定时任务工具实现
"""

import threading
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, Callable, List


class TaskScheduler:
    """定时任务调度器（单例）"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.tasks: Dict[str, dict] = {}
        self.running = False
        self.thread = None
        self.callbacks: List[Callable] = []
    
    def add_callback(self, callback: Callable):
        """添加任务完成回调"""
        self.callbacks.append(callback)
    
    def add_task(self, delay_seconds: int, message: str) -> str:
        """添加定时任务"""
        task_id = str(uuid.uuid4())[:8]
        execute_time = datetime.now() + timedelta(seconds=delay_seconds)
        
        self.tasks[task_id] = {
            "id": task_id,
            "execute_time": execute_time,
            "message": message,
            "delay": delay_seconds,
        }
        
        if not self.running:
            self._start()
        
        return task_id
    
    def _start(self):
        """启动调度器"""
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
    
    def _run(self):
        """调度器主循环"""
        while self.running:
            now = datetime.now()
            to_remove = []
            
            for task_id, task in self.tasks.items():
                if now >= task["execute_time"]:
                    msg = f"⏰ 提醒：{task['message']}"
                    for callback in self.callbacks:
                        try:
                            callback(msg)
                        except Exception:
                            pass
                    to_remove.append(task_id)
            
            for task_id in to_remove:
                del self.tasks[task_id]
            
            time.sleep(0.5)
    
    def stop(self):
        """停止调度器"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)


_scheduler = TaskScheduler()


def create_timer_task(delay_seconds: int = None, seconds: int = None, 
                      duration: int = None, message: str = None, 
                      content: str = None, task: str = None) -> str:
    """
    创建定时任务 - 支持多种参数名
    
    Args:
        delay_seconds: 延迟秒数
        seconds: 延迟秒数（别名）
        duration: 延迟秒数（别名）
        message: 提醒消息
        content: 提醒消息（别名）
        task: 提醒消息（别名）
    
    Returns:
        任务ID
    """
    # 获取延迟秒数（支持多种参数名）
    delay = delay_seconds or seconds or duration
    if delay is None:
        return "错误: 请指定时间参数 (delay_seconds/seconds/duration)"
    
    # 获取消息内容（支持多种参数名）
    msg = message or content or task
    if msg is None:
        return "错误: 请指定提醒内容 (message/content/task)"
    
    # 转换为整数
    try:
        delay = int(delay)
    except ValueError:
        return f"错误: 时间参数必须是数字，当前为: {delay}"
    
    if delay <= 0:
        return "错误: 延迟时间必须大于0秒"
    
    if delay > 86400:
        return "错误: 延迟时间不能超过24小时（86400秒）"
    
    task_id = _scheduler.add_task(delay, msg)
    
    # 计算执行时间
    execute_time = datetime.now() + timedelta(seconds=delay)
    
    return (f"✅ 定时任务已创建！\n"
            f"   任务ID: {task_id}\n"
            f"   提醒内容: {msg}\n"
            f"   将在 {delay} 秒后执行（{execute_time.strftime('%H:%M:%S')}）")


def get_scheduler() -> TaskScheduler:
    """获取调度器实例"""
    return _scheduler