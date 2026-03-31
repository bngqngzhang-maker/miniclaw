"""
主入口 - 支持 .env 文件
"""

import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.config import Config
from core.agent import MiniclawAgent


def load_env():
    """加载 .env 文件"""
    # 尝试加载 .env 文件
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        load_dotenv(env_path)
        print("✅ 已加载 .env 文件")
    else:
        print("⚠️ 未找到 .env 文件，将使用系统环境变量")


def main():
    print("\n🦞 Miniclaw 启动\n")
    
    # 加载环境变量
    load_env()
    
    # 获取 API Key（优先从环境变量，其次从 .env）
    api_key = os.getenv("DASHSCOPE_API_KEY")
    
    if not api_key:
        print("❌ 未找到 DASHSCOPE_API_KEY")
        print("请在 .env 文件中设置: DASHSCOPE_API_KEY=your-api-key")
        print("或使用环境变量: export DASHSCOPE_API_KEY=your-api-key")
        return
    
    # 初始化配置
    config = Config()
    config.dashscope_api_key = api_key
    config.verbose = True
    
    try:
        agent = MiniclawAgent(config=config)
        
        print("\n命令: /clear(清空历史) /skills(查看技能) /quit(退出)\n")
        
        # 对话循环
        while True:
            try:
                user_input = input("\n你: ").strip()
                
                if not user_input:
                    continue
                
                if user_input == "/quit":
                    print("再见！")
                    break
                elif user_input == "/clear":
                    agent.clear_history()
                    print("✅ 历史已清空")
                    continue
                elif user_input == "/skills":
                    print("\n可用技能:")
                    for s in agent.list_skills():
                        print(f"  • {s}")
                    continue
                
                # 正常对话
                agent.chat(user_input)
                
            except KeyboardInterrupt:
                print("\n再见！")
                break
            except Exception as e:
                print(f"错误: {e}")
                
    except Exception as e:
        print(f"初始化失败: {e}")


if __name__ == "__main__":
    main()