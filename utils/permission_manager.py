#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
权限管理工具
用于自动获取和管理程序所需的权限
"""

import os
import sys
import stat
import platform
import subprocess
import shutil
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Union


class 权限管理器:
    """权限管理器类，用于获取和管理程序所需的权限"""
    
    @staticmethod
    def 检查文件权限(文件路径: str) -> Dict[str, bool]:
        """
        检查文件的权限
        
        参数:
            文件路径: 要检查的文件路径
            
        返回:
            包含权限信息的字典
        """
        if not os.path.exists(文件路径):
            return {"存在": False}
        
        # 获取文件状态
        文件状态 = os.stat(文件路径)
        
        # 检查是否可执行
        可执行 = bool(文件状态.st_mode & stat.S_IXUSR)
        
        # 检查是否可读
        可读 = bool(文件状态.st_mode & stat.S_IRUSR)
        
        # 检查是否可写
        可写 = bool(文件状态.st_mode & stat.S_IWUSR)
        
        # 检查是否是当前用户所有
        当前用户 = os.getuid() if hasattr(os, 'getuid') else None
        是否所有者 = 文件状态.st_uid == 当前用户 if 当前用户 is not None else None
        
        return {
            "存在": True,
            "可执行": 可执行,
            "可读": 可读,
            "可写": 可写,
            "是否所有者": 是否所有者
        }
    
    @staticmethod
    def 设置文件可执行(文件路径: str) -> bool:
        """
        设置文件为可执行
        
        参数:
            文件路径: 要设置的文件路径
            
        返回:
            是否设置成功
        """
        try:
            # 获取当前权限
            当前权限 = os.stat(文件路径).st_mode
            
            # 添加可执行权限
            新权限 = 当前权限 | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
            
            # 设置新权限
            os.chmod(文件路径, 新权限)
            
            return True
        except Exception as e:
            print(f"设置文件可执行权限时出错: {str(e)}")
            return False
    
    @staticmethod
    def 设置文件权限(文件路径: str, 可读: bool = True, 可写: bool = True, 可执行: bool = False) -> bool:
        """
        设置文件权限
        
        参数:
            文件路径: 要设置的文件路径
            可读: 是否可读
            可写: 是否可写
            可执行: 是否可执行
            
        返回:
            是否设置成功
        """
        try:
            # 计算权限模式
            模式 = 0
            if 可读:
                模式 |= stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH
            if 可写:
                模式 |= stat.S_IWUSR
            if 可执行:
                模式 |= stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
            
            # 设置权限
            os.chmod(文件路径, 模式)
            
            return True
        except Exception as e:
            print(f"设置文件权限时出错: {str(e)}")
            return False
    
    @staticmethod
    def 检查目录权限(目录路径: str) -> Dict[str, bool]:
        """
        检查目录的权限
        
        参数:
            目录路径: 要检查的目录路径
            
        返回:
            包含权限信息的字典
        """
        if not os.path.exists(目录路径) or not os.path.isdir(目录路径):
            return {"存在": False}
        
        # 获取目录状态
        目录状态 = os.stat(目录路径)
        
        # 检查是否可执行（对目录来说，可执行意味着可以访问其中的文件）
        可执行 = bool(目录状态.st_mode & stat.S_IXUSR)
        
        # 检查是否可读
        可读 = bool(目录状态.st_mode & stat.S_IRUSR)
        
        # 检查是否可写
        可写 = bool(目录状态.st_mode & stat.S_IWUSR)
        
        # 检查是否是当前用户所有
        当前用户 = os.getuid() if hasattr(os, 'getuid') else None
        是否所有者 = 目录状态.st_uid == 当前用户 if 当前用户 is not None else None
        
        # 检查是否可以在目录中创建文件
        可创建文件 = os.access(目录路径, os.W_OK | os.X_OK)
        
        return {
            "存在": True,
            "可执行": 可执行,
            "可读": 可读,
            "可写": 可写,
            "是否所有者": 是否所有者,
            "可创建文件": 可创建文件
        }
    
    @staticmethod
    def 设置目录权限(目录路径: str, 可读: bool = True, 可写: bool = True, 可执行: bool = True) -> bool:
        """
        设置目录权限
        
        参数:
            目录路径: 要设置的目录路径
            可读: 是否可读
            可写: 是否可写
            可执行: 是否可执行
            
        返回:
            是否设置成功
        """
        try:
            # 计算权限模式
            模式 = 0
            if 可读:
                模式 |= stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH
            if 可写:
                模式 |= stat.S_IWUSR
            if 可执行:
                模式 |= stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
            
            # 设置权限
            os.chmod(目录路径, 模式)
            
            return True
        except Exception as e:
            print(f"设置目录权限时出错: {str(e)}")
            return False
    
    @staticmethod
    def 创建目录(目录路径: str, 权限: int = None) -> bool:
        """
        创建目录，如果不存在
        
        参数:
            目录路径: 要创建的目录路径
            权限: 目录权限，如果为None则使用默认权限
            
        返回:
            是否创建成功
        """
        try:
            # 如果目录已存在，直接返回成功
            if os.path.exists(目录路径) and os.path.isdir(目录路径):
                return True
            
            # 创建目录
            if 权限 is None:
                os.makedirs(目录路径, exist_ok=True)
            else:
                os.makedirs(目录路径, mode=权限, exist_ok=True)
            
            return True
        except Exception as e:
            print(f"创建目录时出错: {str(e)}")
            return False
    
    @staticmethod
    def 是否有管理员权限() -> bool:
        """
        检查当前进程是否具有管理员权限
        
        返回:
            是否有管理员权限
        """
        try:
            if platform.system() == "Windows":
                # Windows系统
                import ctypes
                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            else:
                # Unix/Linux/Mac系统
                return os.geteuid() == 0
        except:
            # 如果无法确定，假设没有管理员权限
            return False
    
    @staticmethod
    def 以管理员权限运行(命令: List[str]) -> Tuple[bool, str]:
        """
        以管理员权限运行命令
        
        参数:
            命令: 要运行的命令列表
            
        返回:
            (是否成功, 输出或错误信息)
        """
        try:
            if platform.system() == "Windows":
                # Windows系统
                import ctypes
                import win32con
                import win32event
                import win32process
                from win32com.shell.shell import ShellExecuteEx
                from win32com.shell import shellcon
                
                # 如果已经有管理员权限，直接运行命令
                if 权限管理器.是否有管理员权限():
                    进程 = subprocess.run(命令, capture_output=True, text=True)
                    return 进程.returncode == 0, 进程.stdout if 进程.returncode == 0 else 进程.stderr
                
                # 否则，使用ShellExecuteEx以管理员权限运行
                参数 = ' '.join(f'"{arg}"' for arg in 命令[1:])
                执行信息 = ShellExecuteEx(
                    nShow=win32con.SW_HIDE,
                    fMask=shellcon.SEE_MASK_NOCLOSEPROCESS,
                    lpVerb='runas',  # 请求管理员权限
                    lpFile=命令[0],
                    lpParameters=参数
                )
                
                # 等待进程完成
                进程句柄 = 执行信息['hProcess']
                win32event.WaitForSingleObject(进程句柄, win32event.INFINITE)
                退出码 = win32process.GetExitCodeProcess(进程句柄)
                
                return 退出码 == 0, f"命令已执行，退出码: {退出码}"
            else:
                # Unix/Linux/Mac系统
                if 权限管理器.是否有管理员权限():
                    # 如果已经有管理员权限，直接运行命令
                    进程 = subprocess.run(命令, capture_output=True, text=True)
                    return 进程.returncode == 0, 进程.stdout if 进程.returncode == 0 else 进程.stderr
                else:
                    # 否则，使用sudo运行
                    sudo命令 = ["sudo"]
                    sudo命令.extend(命令)
                    进程 = subprocess.run(sudo命令, capture_output=True, text=True)
                    return 进程.returncode == 0, 进程.stdout if 进程.returncode == 0 else 进程.stderr
        except Exception as e:
            return False, f"以管理员权限运行命令时出错: {str(e)}"
    
    @staticmethod
    def 自动设置脚本可执行(脚本路径: List[str]) -> Dict[str, bool]:
        """
        自动设置多个脚本为可执行
        
        参数:
            脚本路径: 要设置的脚本路径列表
            
        返回:
            包含每个脚本设置结果的字典
        """
        结果 = {}
        
        for 路径 in 脚本路径:
            # 检查文件是否存在
            if not os.path.exists(路径):
                结果[路径] = False
                continue
            
            # 检查当前权限
            权限 = 权限管理器.检查文件权限(路径)
            
            # 如果已经可执行，跳过
            if 权限.get("可执行", False):
                结果[路径] = True
                continue
            
            # 尝试设置可执行权限
            成功 = 权限管理器.设置文件可执行(路径)
            
            # 如果失败且不是所有者，尝试使用管理员权限
            if not 成功 and not 权限.get("是否所有者", True):
                if platform.system() == "Windows":
                    # Windows系统使用icacls命令
                    命令 = ["icacls", 路径, "/grant", f"{os.getlogin()}:F"]
                else:
                    # Unix/Linux/Mac系统使用chmod命令
                    命令 = ["chmod", "+x", 路径]
                
                成功, _ = 权限管理器.以管理员权限运行(命令)
            
            结果[路径] = 成功
        
        return 结果
    
    @staticmethod
    def 自动创建配置目录() -> Tuple[bool, str]:
        """
        自动创建配置目录
        
        返回:
            (是否成功, 配置目录路径)
        """
        # 确定配置目录路径
        主目录 = str(Path.home())
        配置目录 = os.path.join(主目录, ".crypto_wallet")
        
        # 尝试创建目录
        成功 = 权限管理器.创建目录(配置目录)
        
        # 如果失败，尝试使用管理员权限
        if not 成功:
            if platform.system() == "Windows":
                # Windows系统使用mkdir命令
                命令 = ["mkdir", 配置目录]
            else:
                # Unix/Linux/Mac系统使用mkdir命令
                命令 = ["mkdir", "-p", 配置目录]
            
            成功, _ = 权限管理器.以管理员权限运行(命令)
        
        return 成功, 配置目录
    
    @staticmethod
    def 获取当前脚本路径() -> str:
        """
        获取当前脚本的绝对路径
        
        返回:
            当前脚本的绝对路径
        """
        if getattr(sys, 'frozen', False):
            # 如果是打包后的可执行文件
            return os.path.abspath(sys.executable)
        else:
            # 如果是脚本
            return os.path.abspath(sys.argv[0])
    
    @staticmethod
    def 获取脚本目录() -> str:
        """
        获取当前脚本所在的目录
        
        返回:
            当前脚本所在的目录
        """
        脚本路径 = 权限管理器.获取当前脚本路径()
        return os.path.dirname(脚本路径)
    
    @staticmethod
    def 检查并修复权限() -> Dict[str, bool]:
        """
        检查并修复所有脚本的权限
        
        返回:
            包含修复结果的字典
        """
        # 获取脚本目录
        脚本目录 = 权限管理器.获取脚本目录()
        
        # 要检查的脚本列表
        脚本列表 = [
            os.path.join(脚本目录, "crypto_wallet_generator.py"),
            os.path.join(脚本目录, "crypto_wallet_cn_optimized.py"),
            os.path.join(脚本目录, "crypto_wallet_secure_optimized.py"),
            os.path.join(脚本目录, "run_wallet_generator.sh"),
            os.path.join(脚本目录, "run_wallet_generator_mac.command"),
            os.path.join(脚本目录, "tests/run_tests.py")
        ]
        
        # 自动设置脚本可执行
        结果 = 权限管理器.自动设置脚本可执行(脚本列表)
        
        # 创建配置目录
        配置目录成功, 配置目录 = 权限管理器.自动创建配置目录()
        结果["配置目录"] = 配置目录成功
        
        return 结果
    
    @staticmethod
    def 显示权限状态() -> str:
        """
        显示权限状态
        
        返回:
            格式化的权限状态字符串
        """
        # 获取脚本目录
        脚本目录 = 权限管理器.获取脚本目录()
        
        # 要检查的脚本列表
        脚本列表 = [
            os.path.join(脚本目录, "crypto_wallet_generator.py"),
            os.path.join(脚本目录, "crypto_wallet_cn_optimized.py"),
            os.path.join(脚本目录, "crypto_wallet_secure_optimized.py"),
            os.path.join(脚本目录, "run_wallet_generator.sh"),
            os.path.join(脚本目录, "run_wallet_generator_mac.command"),
            os.path.join(脚本目录, "tests/run_tests.py")
        ]
        
        输出 = "===== 权限状态 =====\n\n"
        
        # 检查是否有管理员权限
        管理员权限 = 权限管理器.是否有管理员权限()
        输出 += f"管理员权限: {'是 ✓' if 管理员权限 else '否 ✗'}\n\n"
        
        # 检查脚本权限
        输出 += "脚本权限:\n"
        for 脚本 in 脚本列表:
            if os.path.exists(脚本):
                权限 = 权限管理器.检查文件权限(脚本)
                可执行 = 权限.get("可执行", False)
                状态 = "可执行 ✓" if 可执行 else "不可执行 ✗"
                输出 += f"  - {os.path.basename(脚本)}: {状态}\n"
            else:
                输出 += f"  - {os.path.basename(脚本)}: 不存在 ✗\n"
        
        # 检查配置目录
        主目录 = str(Path.home())
        配置目录 = os.path.join(主目录, ".crypto_wallet")
        配置目录权限 = 权限管理器.检查目录权限(配置目录)
        
        输出 += "\n配置目录:\n"
        if 配置目录权限["存在"]:
            输出 += f"  - 路径: {配置目录}\n"
            输出 += f"  - 可读: {'是 ✓' if 配置目录权限.get('可读', False) else '否 ✗'}\n"
            输出 += f"  - 可写: {'是 ✓' if 配置目录权限.get('可写', False) else '否 ✗'}\n"
            输出 += f"  - 可创建文件: {'是 ✓' if 配置目录权限.get('可创建文件', False) else '否 ✗'}\n"
        else:
            输出 += f"  - 路径: {配置目录} (不存在 ✗)\n"
        
        return 输出


# 测试代码
if __name__ == "__main__":
    print("===== 权限管理器测试 =====\n")
    
    # 显示权限状态
    print(权限管理器.显示权限状态())
    
    # 询问是否修复权限
    print("\n是否自动修复权限问题? (y/n)")
    选择 = input("> ").lower()
    
    if 选择 in ['y', 'yes', '是']:
        结果 = 权限管理器.检查并修复权限()
        
        print("\n修复结果:")
        for 路径, 成功 in 结果.items():
            状态 = "成功 ✓" if 成功 else "失败 ✗"
            print(f"  - {os.path.basename(路径) if 路径 != '配置目录' else '配置目录'}: {状态}")
        
        print("\n修复后的权限状态:")
        print(权限管理器.显示权限状态())