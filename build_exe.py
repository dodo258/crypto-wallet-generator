#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
加密货币钱包助记词生成工具 - 打包脚本
用于将Python程序打包成Windows可执行文件

作者: Crypto Wallet Generator Team
版本: 1.0.0
许可证: MIT
"""

import os
import sys
import shutil
import subprocess
import platform
import argparse

def print_colored(text, color):
    """打印彩色文本"""
    colors = {
        'green': '\033[92m',
        'blue': '\033[94m',
        'yellow': '\033[93m',
        'red': '\033[91m',
        'end': '\033[0m'
    }
    print(f"{colors.get(color, '')}{text}{colors['end']}")

def install_pyinstaller():
    """安装PyInstaller"""
    print_colored("正在安装PyInstaller...", "blue")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print_colored("PyInstaller安装完成", "green")
        return True
    except subprocess.CalledProcessError as e:
        print_colored(f"安装PyInstaller失败: {e}", "red")
        return False

def install_dependencies():
    """安装所有依赖"""
    print_colored("正在安装所有依赖...", "blue")
    try:
        # 安装基础依赖
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        # 安装高级依赖
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements_secure.txt"])
        print_colored("所有依赖安装完成", "green")
        return True
    except subprocess.CalledProcessError as e:
        print_colored(f"安装依赖失败: {e}", "red")
        return False

def build_basic_version():
    """打包基础版本"""
    print_colored("正在打包基础版本...", "blue")
    
    # 确定分隔符
    separator = ";" if platform.system() == "Windows" else ":"
    
    cmd = [
        "pyinstaller",
        "--onefile",
        "--name=crypto_wallet_generator",
        "--add-data=requirements.txt{}".format(separator),
        "crypto_wallet_generator.py"
    ]
    
    try:
        subprocess.check_call(cmd)
        print_colored("基础版本打包完成", "green")
        return True
    except subprocess.CalledProcessError as e:
        print_colored(f"打包基础版本失败: {e}", "red")
        return False

def build_secure_version():
    """打包高安全标准版本"""
    print_colored("正在打包高安全标准版本...", "blue")
    
    # 确定分隔符
    separator = ";" if platform.system() == "Windows" else ":"
    
    cmd = [
        "pyinstaller",
        "--onefile",
        "--name=crypto_wallet_secure",
        "--add-data=requirements_secure.txt{}".format(separator),
        "crypto_wallet_secure_optimized.py"
    ]
    
    try:
        subprocess.check_call(cmd)
        print_colored("高安全标准版本打包完成", "green")
        return True
    except subprocess.CalledProcessError as e:
        print_colored(f"打包高安全标准版本失败: {e}", "red")
        return False

def copy_files_to_dist():
    """复制必要文件到dist目录"""
    print_colored("正在复制必要文件到dist目录...", "blue")
    
    if not os.path.exists("dist"):
        os.makedirs("dist")
    
    # 复制README和LICENSE
    for file in ["README.md", "LICENSE"]:
        if os.path.exists(file):
            shutil.copy(file, os.path.join("dist", file))
    
    # 复制utils目录
    utils_src = "utils"
    utils_dst = os.path.join("dist", "utils")
    
    if os.path.exists(utils_src):
        if os.path.exists(utils_dst):
            shutil.rmtree(utils_dst)
        shutil.copytree(utils_src, utils_dst)
    
    print_colored("文件复制完成", "green")
    return True

def create_launcher():
    """创建启动器"""
    print_colored("正在创建启动器...", "blue")
    
    launcher_content = """@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: 设置终端颜色
set "GREEN=[92m"
set "BLUE=[94m"
set "YELLOW=[93m"
set "RED=[91m"
set "NC=[0m"

:: 清屏
cls

:: 显示欢迎信息
echo %GREEN%================================================%NC%
echo %GREEN%    加密货币钱包助记词生成工具 - Windows版    %NC%
echo %GREEN%================================================%NC%
echo.
echo %BLUE%请选择要使用的版本:%NC%
echo.
echo %YELLOW%1. 基础版本%NC% - 简单的命令行工具，支持基本的助记词生成功能 %RED%(建议只生成一次性钱包使用)%NC%
echo %YELLOW%2. 高安全标准版本%NC% - 提供多源熵、内存安全处理、SLIP-39分割备份等高级安全特性
echo %YELLOW%3. 退出%NC%
echo.
echo %BLUE%请输入选项 (1-3):%NC%
set /p choice=

if "%choice%"=="1" (
    start crypto_wallet_generator.exe
) else if "%choice%"=="2" (
    start crypto_wallet_secure.exe
) else if "%choice%"=="3" (
    exit
) else (
    echo %RED%无效选项，请重新运行程序%NC%
    pause
)
"""
    
    with open(os.path.join("dist", "启动钱包生成工具.bat"), "w", encoding="utf-8") as f:
        f.write(launcher_content)
    
    print_colored("启动器创建完成", "green")
    return True

def create_readme():
    """创建打包版本的README"""
    print_colored("正在创建打包版本的README...", "blue")
    
    readme_content = """# 加密货币钱包助记词生成工具 - Windows可执行版

这是加密货币钱包助记词生成工具的Windows可执行版本，无需安装Python环境即可运行。

## 使用方法

1. 双击运行 `启动钱包生成工具.bat`
2. 在菜单中选择要使用的版本：
   - 基础版本：简单的命令行工具，支持基本的助记词生成功能
   - 高安全标准版本：提供多源熵、内存安全处理、SLIP-39分割备份等高级安全特性

## 注意事项

- 首次运行时，Windows可能会显示安全警告，这是因为程序没有数字签名。请点击"更多信息"，然后选择"仍要运行"。
- 程序运行过程中可能会被杀毒软件误报，这是因为PyInstaller打包的程序有时会被误认为是恶意软件。如果遇到这种情况，请将程序添加到杀毒软件的白名单中。
- 本程序完全在本地运行，不会上传、保存或记录任何生成的助记词或私钥信息。

## 功能说明

详细功能说明请参考原项目的README文件。

## 许可证

本项目采用MIT许可证 - 详见 LICENSE 文件。
"""
    
    with open(os.path.join("dist", "README_WINDOWS.md"), "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    print_colored("README创建完成", "green")
    return True

def create_zip():
    """创建ZIP压缩包"""
    print_colored("正在创建ZIP压缩包...", "blue")
    
    import zipfile
    
    zip_filename = "crypto_wallet_generator_windows.zip"
    
    if os.path.exists(zip_filename):
        os.remove(zip_filename)
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk("dist"):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, "dist")
                zipf.write(file_path, arcname)
    
    print_colored(f"ZIP压缩包创建完成: {zip_filename}", "green")
    return True

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="打包加密货币钱包助记词生成工具为Windows可执行文件")
    parser.add_argument("--skip-deps", action="store_true", help="跳过安装依赖")
    args = parser.parse_args()
    
    # 检查是否在Windows上运行
    if platform.system() != "Windows":
        print_colored("警告: 此脚本应在Windows系统上运行，以生成Windows可执行文件。", "yellow")
        print_colored("在非Windows系统上打包可能会导致兼容性问题。", "yellow")
        
        proceed = input("是否继续? (y/n): ")
        if proceed.lower() != 'y':
            print_colored("打包已取消", "red")
            return
    
    # 安装PyInstaller
    if not install_pyinstaller():
        print_colored("无法安装PyInstaller，打包失败", "red")
        return
    
    # 安装依赖
    if not args.skip_deps:
        if not install_dependencies():
            print_colored("无法安装依赖，打包失败", "red")
            return
    
    # 打包两个版本
    basic_success = build_basic_version()
    secure_success = build_secure_version()
    
    if not (basic_success and secure_success):
        print_colored("打包过程中出现错误", "red")
        return
    
    # 复制必要文件
    if not copy_files_to_dist():
        print_colored("复制文件失败", "red")
        return
    
    # 创建启动器
    if not create_launcher():
        print_colored("创建启动器失败", "red")
        return
    
    # 创建README
    if not create_readme():
        print_colored("创建README失败", "red")
        return
    
    # 创建ZIP压缩包
    if not create_zip():
        print_colored("创建ZIP压缩包失败", "red")
        return
    
    print_colored("\n打包完成！", "green")
    print_colored("可执行文件位于dist目录中。", "green")
    print_colored("ZIP压缩包: crypto_wallet_generator_windows.zip", "green")
    print_colored("\n使用方法:", "blue")
    print_colored("1. 解压ZIP文件", "blue")
    print_colored("2. 运行'启动钱包生成工具.bat'来启动程序", "blue")

if __name__ == "__main__":
    main()