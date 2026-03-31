"""
智能体核心 - 简化版
只实现：加载 Skill 文档、加载 Context 文档、调用模型、执行工具
"""

import os
import json
import re
from typing import Optional, Dict, Any, Tuple
from datetime import datetime

from tools import ToolRegistry
from core.config import Config
from utils.logger import default_logger as logger


class MiniclawAgent:
    """简化的智能体"""
    
    def __init__(
        self,
        config: Optional[Config] = None,
        skills_dir: str = "skills",
        context_dir: str = "context"
    ):
        self.config = config or Config.from_env()
        self.skills_dir = skills_dir
        self.context_dir = context_dir
        
        # 工具注册表
        self.tools = ToolRegistry()
        
        # 加载文档
        self.skills = self._load_skill_docs()
        self.system_prompt = self._load_system_doc()
        
        # 初始化模型客户端
        self._init_qwen()
        
        logger.info(f"✅ 初始化完成，加载 {len(self.skills)} 个 Skills")
    
    def _init_qwen(self):
        """初始化 Qwen"""
        try:
            import dashscope
            from dashscope import Generation
            dashscope.api_key = self.config.dashscope_api_key
            self.generation = Generation
        except ImportError:
            raise Exception("请安装 dashscope: pip install dashscope")
    
    def _load_skill_docs(self) -> Dict[str, str]:
        """加载所有 Skill 文档（.md 文件）"""
        skills = {}
        if not os.path.exists(self.skills_dir):
            os.makedirs(self.skills_dir)
            return skills
        
        for f in os.listdir(self.skills_dir):
            if f.endswith('.md'):
                name = f[:-3]
                with open(os.path.join(self.skills_dir, f), 'r', encoding='utf-8') as file:
                    skills[name] = file.read()
        return skills
    
    def _load_system_doc(self) -> str:
        """加载系统人设文档"""
        path = os.path.join(self.context_dir, "system.md")
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        return "你是 Miniclaw，一个友好的智能助手。"
    
    def _load_conversation_doc(self) -> str:
        """加载对话历史文档"""
        path = os.path.join(self.context_dir, "conversation.md")
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        return ""
    
    def _save_conversation_doc(self, user_msg: str, assistant_msg: str):
        """保存对话到文档"""
        path = os.path.join(self.context_dir, "conversation.md")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        entry = f"""
## {timestamp}

**用户**: {user_msg}

**助手**: {assistant_msg}

---"""
        
        with open(path, 'a', encoding='utf-8') as f:
            f.write(entry)
    
    def _build_prompt(self, user_input: str) -> str:
        """构建提示词"""
        prompt = f"""{self.system_prompt}

## 对话历史
{self._load_conversation_doc()}

## 可用技能
"""
        # 添加技能描述
        for name, content in self.skills.items():
            # 提取技能简介
            lines = content.split('\n')
            desc = ""
            for i, line in enumerate(lines):
                if "## 技能描述" in line and i+1 < len(lines):
                    desc = lines[i+1].strip()
                    break
            prompt += f"\n### {name}\n{desc}\n"
        
        # 添加工具说明
        prompt += f"""
## 可用工具
{self._get_tools_desc()}

## 工具调用格式
需要调用工具时，输出：
<tool>
{{"name": "工具名", "args": {{"参数": "值"}}}}
</tool>

## 当前问题
用户: {user_input}

助手: """
        return prompt
    
    def _get_tools_desc(self) -> str:
        """获取工具描述"""
        desc = ""
        for tool in self.tools.get_tools_description():
            desc += f"- {tool['name']}: {tool['description']}\n"
        return desc
    
    def _parse_tool_call(self, text: str) -> Optional[Tuple[str, Dict]]:
        """解析工具调用"""
        match = re.search(r'<tool>\s*({.*?})\s*</tool>', text, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group(1))
                return data.get('name'), data.get('args', {})
            except:
                pass
        return None
    
    def _call_qwen(self, prompt: str) -> str:
        """调用 Qwen"""
        try:
            response = self.generation.call(
                model=self.config.model_name,
                prompt=prompt,
                temperature=self.config.temperature,
                top_p=self.config.top_p,
                max_tokens=self.config.max_tokens,
                result_format='message'
            )
            
            if response.status_code == 200:
                return response.output.choices[0].message.content
            else:
                return f"模型调用失败: {response.message}"
        except Exception as e:
            return f"错误: {str(e)}"
    
    def chat(self, user_input: str) -> str:
        """处理用户输入"""
        if self.config.verbose:
            logger.info(f"用户: {user_input}")
        
        # 构建提示词
        prompt = self._build_prompt(user_input)
        
        # 调用模型
        response = self._call_qwen(prompt)
        
        # 检查是否需要调用工具
        tool_result = self._parse_tool_call(response)
        
        if tool_result:
            tool_name, args = tool_result
            logger.info(f"调用工具: {tool_name}, 参数: {args}")
            
            # 执行工具
            tool_func = self.tools.get(tool_name)
            if tool_func:
                result = tool_func(**args)
                logger.info(f"工具返回: {result}")
                
                # 用工具结果再次调用模型
                final_prompt = f"""{self.system_prompt}

用户问题: {user_input}

工具执行结果:
{result}

请根据工具结果回答用户。"""
                final_response = self._call_qwen(final_prompt)
            else:
                final_response = f"工具 {tool_name} 不存在"
        else:
            final_response = response
        
        # 保存对话
        self._save_conversation_doc(user_input, final_response)
        
        if self.config.verbose:
            logger.info(f"助手: {final_response}")
        
        return final_response
    
    def clear_history(self):
        """清空对话历史"""
        path = os.path.join(self.context_dir, "conversation.md")
        with open(path, 'w', encoding='utf-8') as f:
            f.write("# 对话历史\n")
        logger.info("对话历史已清空")
    
    def list_skills(self) -> list:
        """列出所有技能"""
        return list(self.skills.keys())