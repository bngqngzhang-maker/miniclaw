Miniclaw - 智能体框架
基于 Qwen-Max 大语言模型的智能体框架，支持文档驱动的 Skill 和 Context 系统，以及工具调用能力。

✨ 特性
🤖 大模型驱动：基于阿里云通义千问 Qwen-Max 模型

📝 文档化 Skill：使用 Markdown 文件定义技能行为

💬 上下文记忆：对话历史自动保存到文档，支持持久化

🔧 工具调用：支持天气查询、网页搜索、定时任务等多种工具

🎯 模块化设计：清晰的目录结构，易于扩展和维护

🌍 免费天气 API：使用 wttr.in 免费天气服务，无需 API Key



📚 模块结构:
miniclaw/
├── main.py                 # 主入口
├── core/
│   ├── agent.py           # 智能体核心
│   └── config.py          # 配置管理
├── skills/                 # Skill 提示词文档
│   ├── weather.md         # 天气查询技能
│   ├── web_search.md      # 网页搜索技能
│   ├── timer.md           # 定时任务技能
│   └── datetime.md        # 时间查询技能
├── context/                # Context 文档
│   ├── system.md          # 系统人设
│   └── conversation.md    # 对话历史（自动生成）
├── tools/                  # 工具实现
│   ├── __init__.py
│   ├── weather_backup.py  # 天气查询（免费 API）
│   ├── web_search.py      # 网页搜索
│   ├── timer.py           # 定时任务
│   └── time_tool.py       # 时间查询
├── utils/
│   └── logger.py          # 日志工具
└── requirements.txt       # 依赖文件




🔄 工作流程:
用户输入
    ↓
加载 Skill 文档（skills/*.md）
    ↓
加载 Context 文档（system.md + conversation.md）
    ↓
构建提示词
    ↓
调用 Qwen-Max 模型
    ↓
解析响应（检查是否包含工具调用）
    ↓
    ├─ 有工具调用 → 执行工具 → 返回结果 → 再次调用模型
    └─ 无工具调用 → 直接返回回复
    ↓
保存对话到 conversation.md
    ↓
返回给用户




1. 环境要求
Python 3.8+

阿里云 DashScope API Key

2. 安装依赖
bash
pip install -r requirements.txt
3. 配置 API Key
创建 .env 文件：

env
# DashScope API Key（必需）
DASHSCOPE_API_KEY=your-dashscope-api-key

# 可选配置
MINICLAW_VERBOSE=true
MINICLAW_MODEL=qwen-max
MINICLAW_TEMPERATURE=0.7
4. 运行
bash
python main.py
💬 使用示例
交互式对话
text
🦞 Miniclaw 启动

命令: /clear(清空历史) /skills(查看技能) /quit(退出)

你: 北京今天天气怎么样？
🤖 miniclaw: 北京|晴|22|45|东北风2级

你: 明天呢？
🤖 miniclaw: 北京|多云|18~25|60|15km/h|星期三

你: 5分钟后提醒我喝水
🤖 miniclaw: ✅ 定时任务已创建！将在 300 秒后提醒：喝水

你: 现在几点了？
🤖 miniclaw: 现在是 2026年3月31日 21:30:00，星期二
交互式命令
命令	说明
/clear	清除对话历史
/skills	查看可用技能列表
/history	查看对话历史
/quit	退出程序
🛠️ 可用工具
1. 天气查询
触发：询问天气相关

支持：今天、明天、后天天气

示例："北京天气"、"明天会下雨吗"

2. 网页搜索
触发：搜索信息、查询知识

示例："什么是LangChain"、"搜索人工智能新闻"

3. 定时任务
触发：设置提醒、倒计时

示例："10秒后提醒我"、"5分钟后叫我"

4. 时间查询
触发：询问当前时间

示例："现在几点"、"今天几号"

📝 自定义 Skill
Skill 是 Markdown 格式的提示词文档，存放在 skills/ 目录：

markdown
# Skill Name

## 技能描述
描述这个技能的功能

## 触发条件
什么情况下使用这个技能

## 技能行为
技能的具体行为逻辑

## 示例对话
用户：...
助手：...
添加新 Skill
在 skills/ 目录创建 .md 文件

定义技能的行为和触发条件

在 tools/ 目录实现对应的工具函数

在 tools/__init__.py 中注册工具

🔧 添加新工具
在 tools/ 目录创建工具文件：

python
# tools/my_tool.py
def my_tool(param: str) -> str:
    """工具描述"""
    # 实现逻辑
    return result
在 tools/__init__.py 中注册：

python
def _register(self):
    from .my_tool import my_tool
    self._tools["my_tool"] = my_tool
在 Skill 文档中描述如何使用这个工具
