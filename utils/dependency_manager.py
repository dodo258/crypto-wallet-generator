#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
依赖管理工具
用于自动检测和安装所需的依赖库
"""

import os
import sys
import subprocess
import importlib
import pkg_resources
from typing import Dict, List, Tuple, Optional, Set


class 依赖管理器:
    """依赖管理器类，用于检测和安装依赖库"""
    
    # 基础依赖
    基础依赖 = {
        "mnemonic": "mnemonic>=0.20",
        "cryptography": "cryptography>=36.0.0"
    }
    
    # 高级依赖
    高级依赖 = {
        "shamir_mnemonic": "shamir-mnemonic>=0.2.0",
        "qrcode": "qrcode[pil]>=7.3.1",
        "pillow": "pillow>=9.0.0",
        "hdwallet": "hdwallet>=2.1.1",
        "base58": "base58>=2.1.1",
        "bech32": "bech32>=1.2.0",
        "ecdsa": "ecdsa>=0.18.0"
    }
    
    # 功能依赖映射
    功能依赖映射 = {
        "基础功能": ["mnemonic", "cryptography"],
        "SLIP-39分割备份": ["shamir_mnemonic"],
        "二维码生成": ["qrcode", "pillow"],
        "钱包地址生成": ["hdwallet", "base58", "bech32", "ecdsa"]
    }
    
    @staticmethod
    def 检查依赖(依赖名称: str) -> bool:
        """
        检查指定依赖是否已安装
        
        参数:
            依赖名称: 要检查的依赖库名称
            
        返回:
            是否已安装
        """
        try:
            importlib.import_module(依赖名称)
            return True
        except ImportError:
            return False
    
    @staticmethod
    def 检查依赖版本(依赖名称: str, 最低版本: Optional[str] = None) -> Tuple[bool, Optional[str]]:
        """
        检查指定依赖的版本是否满足要求
        
        参数:
            依赖名称: 要检查的依赖库名称
            最低版本: 最低要求的版本号，如果为None则只检查是否安装
            
        返回:
            (是否满足要求, 当前版本)
        """
        try:
            # 尝试导入模块
            模块 = importlib.import_module(依赖名称)
            
            # 尝试获取版本号
            版本 = None
            if hasattr(模块, "__version__"):
                版本 = getattr(模块, "__version__")
            elif hasattr(模块, "VERSION"):
                版本 = getattr(模块, "VERSION")
            elif hasattr(模块, "version"):
                版本 = getattr(模块, "version")
            else:
                try:
                    # 使用pkg_resources获取版本
                    版本 = pkg_resources.get_distribution(依赖名称).version
                except:
                    pass
            
            # 如果没有指定最低版本，只要能导入就算满足要求
            if 最低版本 is None:
                return True, 版本
            
            # 如果无法获取版本号，假设满足要求
            if 版本 is None:
                return True, None
            
            # 比较版本号
            当前版本元组 = 依赖管理器.解析版本号(版本)
            最低版本元组 = 依赖管理器.解析版本号(最低版本)
            
            return 当前版本元组 >= 最低版本元组, 版本
        except ImportError:
            return False, None
    
    @staticmethod
    def 解析版本号(版本号: str) -> Tuple[int, ...]:
        """
        解析版本号为元组，用于比较
        
        参数:
            版本号: 版本号字符串，如"1.0.0"
            
        返回:
            版本号元组，如(1, 0, 0)
        """
        try:
            # 移除可能的后缀，如"1.0.0a1"中的"a1"
            版本号 = 版本号.split('-')[0].split('+')[0]
            版本部分 = []
            for 部分 in 版本号.split('.'):
                # 提取数字部分
                数字部分 = ''
                for 字符 in 部分:
                    if 字符.isdigit():
                        数字部分 += 字符
                    else:
                        break
                if 数字部分:
                    版本部分.append(int(数字部分))
                else:
                    版本部分.append(0)
            return tuple(版本部分)
        except:
            return (0, 0, 0)
    
    @staticmethod
    def 安装依赖(依赖规格: str) -> bool:
        """
        安装指定依赖
        
        参数:
            依赖规格: 依赖规格字符串，如"mnemonic>=0.20"
            
        返回:
            是否安装成功
        """
        try:
            print(f"正在安装 {依赖规格}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", 依赖规格])
            return True
        except subprocess.CalledProcessError:
            print(f"安装 {依赖规格} 失败")
            return False
    
    @staticmethod
    def 检查并安装依赖(依赖名称: str, 依赖规格: str) -> bool:
        """
        检查并安装指定依赖
        
        参数:
            依赖名称: 依赖库名称
            依赖规格: 依赖规格字符串，如"mnemonic>=0.20"
            
        返回:
            是否可用（已安装或安装成功）
        """
        # 检查依赖是否已安装
        已安装, 版本 = 依赖管理器.检查依赖版本(依赖名称)
        
        if 已安装:
            print(f"{依赖名称} 已安装 (版本: {版本 or '未知'})")
            return True
        
        # 如果未安装，尝试安装
        print(f"{依赖名称} 未安装，尝试安装...")
        安装成功 = 依赖管理器.安装依赖(依赖规格)
        
        if 安装成功:
            # 再次检查是否安装成功
            已安装, 版本 = 依赖管理器.检查依赖版本(依赖名称)
            if 已安装:
                print(f"{依赖名称} 安装成功 (版本: {版本 or '未知'})")
                return True
        
        print(f"{依赖名称} 安装失败")
        return False
    
    @staticmethod
    def 检查功能依赖(功能名称: str) -> Tuple[bool, List[str]]:
        """
        检查指定功能所需的依赖是否都已安装
        
        参数:
            功能名称: 功能名称，如"SLIP-39分割备份"
            
        返回:
            (是否所有依赖都已安装, 缺失的依赖列表)
        """
        if 功能名称 not in 依赖管理器.功能依赖映射:
            return False, []
        
        依赖列表 = 依赖管理器.功能依赖映射[功能名称]
        缺失依赖 = []
        
        for 依赖名称 in 依赖列表:
            if not 依赖管理器.检查依赖(依赖名称):
                缺失依赖.append(依赖名称)
        
        return len(缺失依赖) == 0, 缺失依赖
    
    @staticmethod
    def 安装功能依赖(功能名称: str) -> bool:
        """
        安装指定功能所需的所有依赖
        
        参数:
            功能名称: 功能名称，如"SLIP-39分割备份"
            
        返回:
            是否所有依赖都安装成功
        """
        if 功能名称 not in 依赖管理器.功能依赖映射:
            return False
        
        依赖列表 = 依赖管理器.功能依赖映射[功能名称]
        全部成功 = True
        
        for 依赖名称 in 依赖列表:
            if 依赖名称 in 依赖管理器.基础依赖:
                依赖规格 = 依赖管理器.基础依赖[依赖名称]
            elif 依赖名称 in 依赖管理器.高级依赖:
                依赖规格 = 依赖管理器.高级依赖[依赖名称]
            else:
                依赖规格 = 依赖名称
            
            if not 依赖管理器.检查并安装依赖(依赖名称, 依赖规格):
                全部成功 = False
        
        return 全部成功
    
    @staticmethod
    def 安装所有基础依赖() -> bool:
        """
        安装所有基础依赖
        
        返回:
            是否所有依赖都安装成功
        """
        全部成功 = True
        
        for 依赖名称, 依赖规格 in 依赖管理器.基础依赖.items():
            if not 依赖管理器.检查并安装依赖(依赖名称, 依赖规格):
                全部成功 = False
        
        return 全部成功
    
    @staticmethod
    def 安装所有高级依赖() -> bool:
        """
        安装所有高级依赖
        
        返回:
            是否所有依赖都安装成功
        """
        全部成功 = True
        
        for 依赖名称, 依赖规格 in 依赖管理器.高级依赖.items():
            if not 依赖管理器.检查并安装依赖(依赖名称, 依赖规格):
                全部成功 = False
        
        return 全部成功
    
    @staticmethod
    def 安装所有依赖() -> bool:
        """
        安装所有依赖（基础和高级）
        
        返回:
            是否所有依赖都安装成功
        """
        基础成功 = 依赖管理器.安装所有基础依赖()
        高级成功 = 依赖管理器.安装所有高级依赖()
        
        return 基础成功 and 高级成功
    
    @staticmethod
    def 从文件安装依赖(文件路径: str) -> bool:
        """
        从requirements文件安装依赖
        
        参数:
            文件路径: requirements文件路径
            
        返回:
            是否安装成功
        """
        try:
            print(f"正在从 {文件路径} 安装依赖...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", 文件路径])
            return True
        except subprocess.CalledProcessError:
            print(f"从 {文件路径} 安装依赖失败")
            return False
    
    @staticmethod
    def 获取已安装依赖() -> Dict[str, str]:
        """
        获取已安装的依赖及其版本
        
        返回:
            依赖名称到版本的映射
        """
        已安装依赖 = {}
        
        # 检查基础依赖
        for 依赖名称 in 依赖管理器.基础依赖:
            已安装, 版本 = 依赖管理器.检查依赖版本(依赖名称)
            if 已安装:
                已安装依赖[依赖名称] = 版本 or "未知"
        
        # 检查高级依赖
        for 依赖名称 in 依赖管理器.高级依赖:
            已安装, 版本 = 依赖管理器.检查依赖版本(依赖名称)
            if 已安装:
                已安装依赖[依赖名称] = 版本 or "未知"
        
        return 已安装依赖
    
    @staticmethod
    def 获取功能可用性() -> Dict[str, bool]:
        """
        获取各功能的可用性
        
        返回:
            功能名称到可用性的映射
        """
        功能可用性 = {}
        
        for 功能名称 in 依赖管理器.功能依赖映射:
            可用, _ = 依赖管理器.检查功能依赖(功能名称)
            功能可用性[功能名称] = 可用
        
        return 功能可用性
    
    @staticmethod
    def 显示依赖状态() -> str:
        """
        显示依赖状态
        
        返回:
            格式化的依赖状态字符串
        """
        已安装依赖 = 依赖管理器.获取已安装依赖()
        功能可用性 = 依赖管理器.获取功能可用性()
        
        输出 = "===== 依赖状态 =====\n\n"
        
        # 显示已安装依赖
        输出 += "已安装依赖:\n"
        for 依赖名称, 版本 in 已安装依赖.items():
            输出 += f"  - {依赖名称}: {版本}\n"
        
        # 显示缺失依赖
        缺失依赖 = set()
        for 依赖名称 in list(依赖管理器.基础依赖.keys()) + list(依赖管理器.高级依赖.keys()):
            if 依赖名称 not in 已安装依赖:
                缺失依赖.add(依赖名称)
        
        if 缺失依赖:
            输出 += "\n缺失依赖:\n"
            for 依赖名称 in 缺失依赖:
                输出 += f"  - {依赖名称}\n"
        
        # 显示功能可用性
        输出 += "\n功能可用性:\n"
        for 功能名称, 可用 in 功能可用性.items():
            状态 = "可用" if 可用 else "不可用"
            输出 += f"  - {功能名称}: {状态}\n"
            
            # 如果功能不可用，显示缺失的依赖
            if not 可用:
                _, 缺失 = 依赖管理器.检查功能依赖(功能名称)
                if 缺失:
                    输出 += f"    缺失依赖: {', '.join(缺失)}\n"
        
        return 输出


# 测试代码
if __name__ == "__main__":
    print("===== 依赖管理器测试 =====\n")
    
    # 显示依赖状态
    print(依赖管理器.显示依赖状态())
    
    # 询问是否安装缺失依赖
    print("\n是否安装所有缺失依赖? (y/n)")
    选择 = input("> ").lower()
    
    if 选择 in ['y', 'yes', '是']:
        依赖管理器.安装所有依赖()
        print("\n安装后的依赖状态:")
        print(依赖管理器.显示依赖状态())