#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
加密货币钱包助记词生成工具 - 全自动依赖安装脚本
为不熟悉命令行的用户提供简单的依赖安装方式

作者: Crypto Wallet Generator Team
版本: 1.0.0
许可证: MIT
"""

import os
import sys
import subprocess
import platform
import time
import random

# 设置颜色输出
class 颜色:
    GREEN = '\033[92m' if platform.system() != "Windows" else ''
    BLUE = '\033[94m' if platform.system() != "Windows" else ''
    YELLOW = '\033[93m' if platform.system() != "Windows" else ''
    RED = '\033[91m' if platform.system() != "Windows" else ''
    END = '\033[0m' if platform.system() != "Windows" else ''

def 打印彩色文本(文本, 颜色代码):
    """打印彩色文本"""
    print(f"{颜色代码}{文本}{颜色.END}")

def 检查Python版本():
    """检查Python版本是否满足要求"""
    打印彩色文本("正在检查Python版本...", 颜色.BLUE)
    
    版本 = sys.version_info
    if 版本.major < 3 or (版本.major == 3 and 版本.minor < 7):
        打印彩色文本(f"警告: 检测到Python版本 {版本.major}.{版本.minor}.{版本.micro}", 颜色.RED)
        打印彩色文本("此工具需要Python 3.7或更高版本。", 颜色.RED)
        
        if platform.system() == "Windows":
            打印彩色文本("请访问 https://www.python.org/downloads/ 下载并安装最新版本的Python。", 颜色.YELLOW)
        elif platform.system() == "Darwin":  # macOS
            打印彩色文本("请使用Homebrew安装Python: brew install python", 颜色.YELLOW)
        else:  # Linux
            打印彩色文本("请使用系统包管理器安装Python 3.7+", 颜色.YELLOW)
            打印彩色文本("Ubuntu/Debian: sudo apt install python3", 颜色.YELLOW)
            打印彩色文本("Fedora: sudo dnf install python3", 颜色.YELLOW)
        
        return False
    else:
        打印彩色文本(f"检测到Python版本 {版本.major}.{版本.minor}.{版本.micro} ✓", 颜色.GREEN)
        return True

def 检查pip():
    """检查pip是否可用"""
    打印彩色文本("正在检查pip...", 颜色.BLUE)
    
    try:
        # 尝试运行pip --version
        subprocess.run([sys.executable, "-m", "pip", "--version"], 
                      check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        打印彩色文本("pip可用 ✓", 颜色.GREEN)
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        打印彩色文本("pip不可用，尝试安装...", 颜色.YELLOW)
        
        try:
            # 尝试安装pip
            subprocess.run([sys.executable, "-m", "ensurepip", "--upgrade"], 
                          check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            打印彩色文本("pip安装成功 ✓", 颜色.GREEN)
            return True
        except subprocess.SubprocessError:
            打印彩色文本("无法安装pip。请手动安装pip后重试。", 颜色.RED)
            
            if platform.system() == "Windows":
                打印彩色文本("请访问 https://pip.pypa.io/en/stable/installation/ 获取安装指南", 颜色.YELLOW)
            elif platform.system() == "Darwin":  # macOS
                打印彩色文本("请运行: curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && python3 get-pip.py", 颜色.YELLOW)
            else:  # Linux
                打印彩色文本("请运行: sudo apt install python3-pip (Ubuntu/Debian)", 颜色.YELLOW)
                打印彩色文本("或: sudo dnf install python3-pip (Fedora)", 颜色.YELLOW)
            
            return False

def 获取最佳镜像源():
    """获取最佳pip镜像源"""
    打印彩色文本("正在测试pip镜像源速度...", 颜色.BLUE)
    
    镜像源列表 = [
        "https://pypi.org/simple",  # 官方源
        "https://pypi.tuna.tsinghua.edu.cn/simple",  # 清华大学镜像
        "https://mirrors.aliyun.com/pypi/simple",  # 阿里云镜像
        "https://mirrors.cloud.tencent.com/pypi/simple",  # 腾讯云镜像
        "https://repo.huaweicloud.com/repository/pypi/simple",  # 华为云镜像
        "https://mirror.baidu.com/pypi/simple"  # 百度镜像
    ]
    
    最佳镜像源 = 镜像源列表[0]  # 默认使用官方源
    最快速度 = float('inf')
    
    for 镜像源 in 镜像源列表:
        开始时间 = time.time()
        try:
            # 尝试连接镜像源
            命令 = [sys.executable, "-m", "pip", "search", "pip", "--index", 镜像源]
            result = subprocess.run(命令, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5)
            
            if result.returncode == 0:
                耗时 = time.time() - 开始时间
                打印彩色文本(f"镜像源 {镜像源} 响应时间: {耗时:.2f}秒", 颜色.BLUE)
                
                if 耗时 < 最快速度:
                    最快速度 = 耗时
                    最佳镜像源 = 镜像源
        except (subprocess.SubprocessError, subprocess.TimeoutExpired):
            打印彩色文本(f"镜像源 {镜像源} 连接失败", 颜色.YELLOW)
    
    打印彩色文本(f"选择最佳镜像源: {最佳镜像源}", 颜色.GREEN)
    return 最佳镜像源

def 安装依赖(依赖文件, 镜像源=None):
    """安装指定依赖文件中的所有依赖"""
    打印彩色文本(f"正在安装依赖 ({依赖文件})...", 颜色.BLUE)
    
    # 构建安装命令
    命令 = [sys.executable, "-m", "pip", "install", "--no-warn-script-location", "-r", 依赖文件]
    
    # 如果指定了镜像源，添加镜像源参数
    if 镜像源:
        命令.extend(["--index-url", 镜像源])
    
    # 执行安装命令
    try:
        subprocess.run(命令, check=True)
        打印彩色文本(f"依赖安装成功 ✓", 颜色.GREEN)
        return True
    except subprocess.SubprocessError as e:
        打印彩色文本(f"依赖安装失败: {str(e)}", 颜色.RED)
        
        # 尝试单独安装每个依赖
        打印彩色文本("尝试单独安装每个依赖...", 颜色.YELLOW)
        成功 = True
        
        with open(依赖文件, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                打印彩色文本(f"正在安装 {line}...", 颜色.BLUE)
                try:
                    单独命令 = [sys.executable, "-m", "pip", "install", "--no-warn-script-location", line]
                    if 镜像源:
                        单独命令.extend(["--index-url", 镜像源])
                    
                    subprocess.run(单独命令, check=True)
                    打印彩色文本(f"{line} 安装成功 ✓", 颜色.GREEN)
                except subprocess.SubprocessError:
                    打印彩色文本(f"{line} 安装失败 ✗", 颜色.RED)
                    成功 = False
        
        return 成功

def 主程序():
    """主程序入口"""
    打印彩色文本("=" * 60, 颜色.GREEN)
    打印彩色文本("    加密货币钱包助记词生成工具 - 全自动依赖安装    ", 颜色.GREEN)
    打印彩色文本("=" * 60, 颜色.GREEN)
    print()
    
    # 检查Python版本
    if not 检查Python版本():
        input("\n按回车键退出...")
        return
    
    # 检查pip
    if not 检查pip():
        input("\n按回车键退出...")
        return
    
    # 获取最佳镜像源
    镜像源 = 获取最佳镜像源()
    
    # 检查requirements.txt和requirements_secure.txt是否存在
    基础依赖文件 = "requirements.txt"
    高级依赖文件 = "requirements_secure.txt"
    
    if not os.path.exists(基础依赖文件):
        打印彩色文本(f"错误: 找不到{基础依赖文件}文件", 颜色.RED)
        input("\n按回车键退出...")
        return
    
    # 安装基础依赖
    打印彩色文本("\n第1步: 安装基础依赖", 颜色.BLUE)
    基础依赖成功 = 安装依赖(基础依赖文件, 镜像源)
    
    # 安装高级依赖（如果存在）
    高级依赖成功 = True
    if os.path.exists(高级依赖文件):
        打印彩色文本("\n第2步: 安装高级依赖", 颜色.BLUE)
        高级依赖成功 = 安装依赖(高级依赖文件, 镜像源)
    
    # 显示安装结果
    print()
    打印彩色文本("=" * 60, 颜色.GREEN)
    打印彩色文本("    安装结果    ", 颜色.GREEN)
    打印彩色文本("=" * 60, 颜色.GREEN)
    
    if 基础依赖成功:
        打印彩色文本("基础依赖: 安装成功 ✓", 颜色.GREEN)
    else:
        打印彩色文本("基础依赖: 安装失败 ✗", 颜色.RED)
    
    if os.path.exists(高级依赖文件):
        if 高级依赖成功:
            打印彩色文本("高级依赖: 安装成功 ✓", 颜色.GREEN)
        else:
            打印彩色文本("高级依赖: 安装失败 ✗", 颜色.RED)
    
    print()
    if 基础依赖成功 and 高级依赖成功:
        打印彩色文本("所有依赖安装成功！您现在可以运行钱包生成工具了。", 颜色.GREEN)
        
        # 显示运行指南
        print()
        打印彩色文本("运行指南:", 颜色.BLUE)
        if platform.system() == "Windows":
            打印彩色文本("请使用虚拟机安装Ubuntu 20.04/22.04并在其中运行程序", 颜色.YELLOW)
        elif platform.system() == "Darwin":  # macOS
            打印彩色文本("运行命令: ./run_wallet_generator_mac.command", 颜色.YELLOW)
        else:  # Linux
            打印彩色文本("运行命令: ./run_wallet_generator_linux.sh", 颜色.YELLOW)
    else:
        打印彩色文本("部分依赖安装失败。请检查错误信息并手动安装缺失的依赖。", 颜色.RED)
    
    input("\n按回车键退出...")

if __name__ == "__main__":
    主程序()