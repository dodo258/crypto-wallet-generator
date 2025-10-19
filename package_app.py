#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
加密货币钱包助记词生成工具 - 打包脚本
使用PyInstaller将程序打包成独立可执行文件

作者: Crypto Wallet Generator Team
版本: 1.0.0
许可证: MIT
"""

import os
import sys
import subprocess
import platform
import shutil
import time

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

def 检查PyInstaller():
    """检查PyInstaller是否已安装"""
    打印彩色文本("正在检查PyInstaller...", 颜色.BLUE)
    
    try:
        # 尝试导入PyInstaller
        import PyInstaller
        打印彩色文本("PyInstaller已安装 ✓", 颜色.GREEN)
        return True
    except ImportError:
        打印彩色文本("PyInstaller未安装，正在安装...", 颜色.YELLOW)
        
        try:
            # 安装PyInstaller
            subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
            打印彩色文本("PyInstaller安装成功 ✓", 颜色.GREEN)
            return True
        except subprocess.SubprocessError:
            打印彩色文本("PyInstaller安装失败 ✗", 颜色.RED)
            打印彩色文本("请手动安装PyInstaller: pip install pyinstaller", 颜色.YELLOW)
            return False

def 检查依赖():
    """检查所有依赖是否已安装"""
    打印彩色文本("正在检查依赖...", 颜色.BLUE)
    
    # 读取requirements.txt和requirements_secure.txt
    所有依赖 = []
    
    for 文件名 in ["requirements.txt", "requirements_secure.txt"]:
        if os.path.exists(文件名):
            with open(文件名, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # 提取包名（去掉版本信息）
                        包名 = line.split('>=')[0].split('==')[0].split('<')[0].strip()
                        所有依赖.append(包名)
    
    # 检查每个依赖
    缺失依赖 = []
    for 依赖 in 所有依赖:
        try:
            __import__(依赖)
            打印彩色文本(f"{依赖} 已安装 ✓", 颜色.GREEN)
        except ImportError:
            打印彩色文本(f"{依赖} 未安装 ✗", 颜色.RED)
            缺失依赖.append(依赖)
    
    if 缺失依赖:
        打印彩色文本("\n检测到缺失的依赖，正在安装...", 颜色.YELLOW)
        for 依赖 in 缺失依赖:
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", 依赖], check=True)
                打印彩色文本(f"{依赖} 安装成功 ✓", 颜色.GREEN)
            except subprocess.SubprocessError:
                打印彩色文本(f"{依赖} 安装失败 ✗", 颜色.RED)
                return False
    
    return True

def 创建启动器(目标目录):
    """创建启动器脚本"""
    打印彩色文本("正在创建启动器...", 颜色.BLUE)
    
    # 根据操作系统创建不同的启动器
    if platform.system() == "Windows":
        启动器路径 = os.path.join(目标目录, "启动钱包生成工具.bat")
        with open(启动器路径, 'w', encoding='utf-8') as f:
            f.write('@echo off\n')
            f.write('echo 正在启动加密货币钱包助记词生成工具...\n')
            f.write('start crypto_wallet_secure.exe\n')
        打印彩色文本(f"Windows启动器已创建: {启动器路径} ✓", 颜色.GREEN)
    
    elif platform.system() == "Darwin":  # macOS
        启动器路径 = os.path.join(目标目录, "启动钱包生成工具.command")
        with open(启动器路径, 'w') as f:
            f.write('#!/bin/bash\n')
            f.write('cd "$(dirname "$0")"\n')
            f.write('echo "正在启动加密货币钱包助记词生成工具..."\n')
            f.write('./crypto_wallet_secure\n')
        # 设置可执行权限
        os.chmod(启动器路径, 0o755)
        打印彩色文本(f"macOS启动器已创建: {启动器路径} ✓", 颜色.GREEN)
    
    else:  # Linux
        启动器路径 = os.path.join(目标目录, "启动钱包生成工具.sh")
        with open(启动器路径, 'w') as f:
            f.write('#!/bin/bash\n')
            f.write('cd "$(dirname "$0")"\n')
            f.write('echo "正在启动加密货币钱包助记词生成工具..."\n')
            f.write('./crypto_wallet_secure\n')
        # 设置可执行权限
        os.chmod(启动器路径, 0o755)
        打印彩色文本(f"Linux启动器已创建: {启动器路径} ✓", 颜色.GREEN)
    
    return 启动器路径

def 复制文档(目标目录):
    """复制README和LICENSE文件到目标目录"""
    打印彩色文本("正在复制文档文件...", 颜色.BLUE)
    
    for 文件名 in ["README.md", "LICENSE"]:
        if os.path.exists(文件名):
            目标路径 = os.path.join(目标目录, 文件名)
            shutil.copy(文件名, 目标路径)
            打印彩色文本(f"{文件名} 已复制 ✓", 颜色.GREEN)

def 打包程序(目标目录):
    """使用PyInstaller打包程序"""
    打印彩色文本("正在使用PyInstaller打包程序...", 颜色.BLUE)
    
    # 构建PyInstaller命令
    命令 = [
        "pyinstaller",
        "--onefile",  # 生成单个可执行文件
        "--clean",    # 清理临时文件
        "--name=crypto_wallet_secure",  # 输出文件名
        "--distpath=" + 目标目录,  # 输出目录
        "--add-data=utils" + os.pathsep + "utils",  # 添加utils目录
    ]
    
    # 添加图标（如果存在）
    if os.path.exists("icon.ico"):
        命令.append("--icon=icon.ico")
    
    # 添加主程序文件
    命令.append("crypto_wallet_secure_optimized.py")
    
    # 执行PyInstaller命令
    try:
        subprocess.run(命令, check=True)
        打印彩色文本("程序打包成功 ✓", 颜色.GREEN)
        return True
    except subprocess.SubprocessError as e:
        打印彩色文本(f"程序打包失败: {str(e)} ✗", 颜色.RED)
        return False

def 创建自述文件(目标目录):
    """创建简化的自述文件"""
    打印彩色文本("正在创建自述文件...", 颜色.BLUE)
    
    自述文件路径 = os.path.join(目标目录, "使用说明.txt")
    with open(自述文件路径, 'w', encoding='utf-8') as f:
        f.write("加密货币钱包助记词生成工具 - 使用说明\n")
        f.write("==============================\n\n")
        f.write("本程序用于安全生成和管理加密货币钱包助记词。\n\n")
        f.write("使用方法：\n")
        
        if platform.system() == "Windows":
            f.write("1. 双击运行 '启动钱包生成工具.bat'\n")
        elif platform.system() == "Darwin":  # macOS
            f.write("1. 双击运行 '启动钱包生成工具.command'\n")
        else:  # Linux
            f.write("1. 运行 './启动钱包生成工具.sh'\n")
        
        f.write("2. 按照程序提示进行操作\n\n")
        f.write("安全提示：\n")
        f.write("- 建议在离线环境中使用本工具\n")
        f.write("- 妥善保管生成的助记词，不要分享给他人\n")
        f.write("- 考虑使用SLIP-39分割备份增强安全性\n\n")
        f.write("详细文档请参阅 README.md 文件\n")
    
    打印彩色文本(f"自述文件已创建: {自述文件路径} ✓", 颜色.GREEN)

def 创建压缩包(目标目录):
    """创建最终的压缩包"""
    打印彩色文本("正在创建最终压缩包...", 颜色.BLUE)
    
    # 获取当前时间戳
    时间戳 = time.strftime("%Y%m%d_%H%M%S")
    
    # 确定操作系统
    if platform.system() == "Windows":
        系统名 = "windows"
    elif platform.system() == "Darwin":  # macOS
        系统名 = "macos"
    else:  # Linux
        系统名 = "linux"
    
    # 创建压缩包名称
    压缩包名称 = f"crypto_wallet_generator_{系统名}_{时间戳}"
    
    # 创建压缩包
    if platform.system() == "Windows":
        # 使用zip命令
        压缩包路径 = os.path.abspath(f"{压缩包名称}.zip")
        shutil.make_archive(压缩包名称, 'zip', 目标目录)
    else:
        # 使用tar命令
        压缩包路径 = os.path.abspath(f"{压缩包名称}.tar.gz")
        shutil.make_archive(压缩包名称, 'gztar', 目标目录)
    
    打印彩色文本(f"压缩包已创建: {压缩包路径} ✓", 颜色.GREEN)
    return 压缩包路径

def 主程序():
    """主程序入口"""
    打印彩色文本("=" * 60, 颜色.GREEN)
    打印彩色文本("    加密货币钱包助记词生成工具 - 打包程序    ", 颜色.GREEN)
    打印彩色文本("=" * 60, 颜色.GREEN)
    print()
    
    # 检查PyInstaller
    if not 检查PyInstaller():
        input("\n按回车键退出...")
        return
    
    # 检查依赖
    if not 检查依赖():
        打印彩色文本("依赖检查失败，打包可能不完整", 颜色.YELLOW)
        继续 = input("是否继续打包? (y/n): ").lower()
        if 继续 != 'y':
            return
    
    # 创建输出目录
    目标目录 = "dist"
    if os.path.exists(目标目录):
        shutil.rmtree(目标目录)
    os.makedirs(目标目录)
    
    # 打包程序
    if not 打包程序(目标目录):
        打印彩色文本("打包失败，请检查错误信息", 颜色.RED)
        input("\n按回车键退出...")
        return
    
    # 创建启动器
    启动器路径 = 创建启动器(目标目录)
    
    # 复制文档
    复制文档(目标目录)
    
    # 创建自述文件
    创建自述文件(目标目录)
    
    # 创建压缩包
    压缩包路径 = 创建压缩包(目标目录)
    
    # 显示完成信息
    print()
    打印彩色文本("=" * 60, 颜色.GREEN)
    打印彩色文本("    打包完成    ", 颜色.GREEN)
    打印彩色文本("=" * 60, 颜色.GREEN)
    print()
    打印彩色文本(f"可执行文件位于: {os.path.join(目标目录, 'crypto_wallet_secure' + ('.exe' if platform.system() == 'Windows' else ''))}", 颜色.BLUE)
    打印彩色文本(f"启动器位于: {启动器路径}", 颜色.BLUE)
    打印彩色文本(f"压缩包位于: {压缩包路径}", 颜色.BLUE)
    print()
    打印彩色文本("使用说明:", 颜色.YELLOW)
    打印彩色文本("1. 解压压缩包到任意位置", 颜色.YELLOW)
    打印彩色文本("2. 运行启动器即可使用程序", 颜色.YELLOW)
    
    input("\n按回车键退出...")

if __name__ == "__main__":
    主程序()