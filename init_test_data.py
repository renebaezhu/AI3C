"""
初始化测试数据脚本
用于创建测试用户和示例Prompts
"""
import os
import sys
from datetime import datetime, timedelta
import random
import json

# 确保能够导入backend模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.models.user import User
from backend.models.prompt import Prompt
from backend.models.data import PromptResult
from backend.utils.db import init_db

def init_test_data():
    """初始化测试数据"""
    print("正在初始化数据库...")
    init_db()
    
    print("正在创建测试用户...")
    try:
        # 创建测试用户
        test_user = User.create(
            username="testuser",
            password="password123",
            email="test@example.com"
        )
        print(f"创建测试用户成功: {test_user.username}")
    except ValueError as e:
        # 如果用户已存在则获取它
        print(f"测试用户已存在: {str(e)}")
        test_user = User.get_by_username("testuser")
    
    # 示例Prompt分类
    categories = ["text-generation", "image-generation", "translation", "qa", "other"]
    
    # 示例标签
    all_tags = ["AI", "GPT", "DALL-E", "翻译", "文本生成", "图像生成", "问答", "助手", 
               "创意写作", "代码", "营销", "教育", "总结", "会话", "编辑"]
    
    print("正在创建示例Prompts...")
    
    # 创建20个示例Prompts
    for i in range(1, 21):
        category = random.choice(categories)
        # 为每个Prompt随机选择2-4个标签
        tags = random.sample(all_tags, random.randint(2, 4))
        
        title = f"示例Prompt {i} - {category.capitalize()}"
        
        # 根据分类生成不同的示例内容
        if category == "text-generation":
            content = f"请生成一篇关于{random.choice(['AI技术', '机器学习', '深度学习', '自然语言处理', '计算机视觉'])}的文章，包含以下要点：\n\n1. 技术背景\n2. 应用场景\n3. 未来发展\n\n要求：字数800字左右，语言通俗易懂。"
        elif category == "image-generation":
            content = f"请生成一张{random.choice(['科幻城市', '未来机器人', '太空旅行', '深海探险', '魔法森林'])}的图像。风格：{random.choice(['写实', '卡通', '水彩', '油画', '像素艺术'])}。"
        elif category == "translation":
            content = f"请将以下{random.choice(['英文', '中文', '法文', '德文', '日文'])}文本翻译成{random.choice(['中文', '英文', '法文', '德文', '日文'])}，保持原文的语气和风格。"
        elif category == "qa":
            content = f"作为一个{random.choice(['历史', '科学', '文学', '技术', '医疗'])}专家，请回答关于{random.choice(['古代文明', '量子力学', '经典文学', '人工智能', '健康饮食'])}的问题。提供详细解释和相关例子。"
        else:
            content = f"系统提示：你是一个专业的{random.choice(['写作助手', '教育顾问', '营销专家', '技术顾问', '创意导师'])}。\n\n用户指令：{random.choice(['帮我优化这篇文章', '解释这个概念', '为我的产品想创意', '解决这个技术问题', '给我一些灵感'])}\n\n附加要求：回复要{random.choice(['简洁', '详细', '专业', '创意', '实用'])}。"
        
        # 创建Prompt
        try:
            prompt = Prompt.create(
                title=title,
                content=content,
                category=category,
                tags=tags,
                user_id=test_user.id
            )
            print(f"创建Prompt成功: {prompt.title}")
            
            # 为每个Prompt创建3-8个执行结果
            results_count = random.randint(3, 8)
            for j in range(results_count):
                # 创建过去30天内的随机日期
                days_ago = random.randint(0, 30)
                created_at = datetime.now() - timedelta(days=days_ago)
                
                # 随机执行时间(200-2000ms)
                execution_time = random.uniform(200, 2000)
                
                # 80%的成功率
                success = random.random() < 0.8
                
                # 创建输入数据
                input_data = f"用户输入样本 {j+1} 针对Prompt: {prompt.title}"
                
                # 创建输出数据
                if success:
                    output_data = f"AI生成的响应 {j+1} 针对输入: {input_data}"
                    error_message = None
                else:
                    output_data = ""
                    error_message = random.choice([
                        "模型超时",
                        "内容过滤触发",
                        "API调用失败",
                        "参数错误",
                        "服务暂时不可用"
                    ])
                
                # 创建结果记录
                PromptResult.create(
                    prompt_id=prompt.id,
                    input_data=input_data,
                    output_data=output_data,
                    execution_time=execution_time,
                    success=success,
                    error_message=error_message
                )
            
            print(f"为Prompt '{prompt.title}' 创建了 {results_count} 个测试结果")
            
        except Exception as e:
            print(f"创建Prompt失败: {str(e)}")
    
    print("测试数据初始化完成!")

if __name__ == "__main__":
    init_test_data() 