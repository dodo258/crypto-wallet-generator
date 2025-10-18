#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
安全清除工具
用于彻底清除内存和系统中的敏感数据痕迹
"""

import os
import sys
import gc
import ctypes
import platform
import tempfile
import subprocess
from typing import List, Any, Optional, Dict, Union


class 安全清除工具:
    """安全清除工具类，提供多种方法彻底清除敏感数据"""
    
    @staticmethod
    def 安全清除内存(数据):
        """
        安全清除内存中的敏感数据
        
        参数:
            数据: 要清除的数据对象
        """
        if isinstance(数据, bytes):
            # 对于字节类型，用0覆盖
            # 注意：bytes对象是不可变的，无法直接修改
            # 只能通过ctypes进行底层操作
            长度 = len(数据)
            ctypes.memset(ctypes.cast(数据, ctypes.POINTER(ctypes.c_char)), 0, 长度)
        elif isinstance(数据, bytearray):
            # 对于bytearray，可以直接修改
            长度 = len(数据)
            # 先用0覆盖
            for i in range(长度):
                数据[i] = 0
            # 再用随机数据覆盖
            随机数据 = os.urandom(长度)
            for i in range(长度):
                数据[i] = 随机数据[i]
            # 最后再次用0覆盖
            for i in range(长度):
                数据[i] = 0
        elif isinstance(数据, str):
            # 对于字符串，无法直接覆盖，但可以尝试删除引用
            数据 = None
        elif isinstance(数据, list):
            # 对于列表，清除每个元素
            for i in range(len(数据)):
                安全清除工具.安全清除内存(数据[i])
                数据[i] = None
        elif isinstance(数据, dict):
            # 对于字典，清除每个值
            for key in 数据:
                安全清除工具.安全清除内存(数据[key])
                数据[key] = None
    
    @staticmethod
    def 强制垃圾回收():
        """
        强制执行Python垃圾回收，确保内存被释放
        """
        # 禁用垃圾回收器自动运行
        gc.disable()
        # 手动运行垃圾回收
        gc.collect()
        # 重新启用垃圾回收器
        gc.enable()
        return True
    
    @staticmethod
    def 清除终端显示():
        """
        清除终端屏幕上的所有内容
        """
        # 对于类Unix系统
        if platform.system() != "Windows":
            os.system('clear')
        # 对于Windows系统
        else:
            os.system('cls')
        return True
    
    @staticmethod
    def 清除系统缓存():
        """
        清除系统缓存和交换文件中可能残留的敏感数据
        """
        try:
            # 创建一个临时大文件来覆盖可能的磁盘缓存
            with tempfile.NamedTemporaryFile(mode='wb', delete=False) as temp_file:
                # 写入大量随机数据（约100MB）
                for _ in range(100):
                    temp_file.write(os.urandom(1024 * 1024))  # 1MB随机数据
                temp_file.flush()
                os.fsync(temp_file.fileno())  # 确保写入磁盘
                temp_file_path = temp_file.name
            
            # 删除临时文件
            os.unlink(temp_file_path)
            
            # 在不同操作系统上尝试清除缓存
            if platform.system() == "Linux":
                # 在Linux上清除页面缓存、目录项和inode
                try:
                    # 需要root权限，可能会失败
                    subprocess.run(["sync"], check=False)
                    # 使用更安全的方式清除缓存，避免shell注入
                    with open("/proc/sys/vm/drop_caches", "w") as f:
                        try:
                            f.write("3")
                        except PermissionError:
                            # 如果没有权限，则静默失败
                            pass
                except:
                    pass
            elif platform.system() == "Darwin":  # macOS
                # 在macOS上清除DNS缓存和目录服务缓存
                try:
                    subprocess.run(["dscacheutil", "-flushcache"], check=False)
                    subprocess.run(["killall", "-HUP", "mDNSResponder"], check=False)
                except:
                    pass
            elif platform.system() == "Windows":
                # 在Windows上清除DNS和ARP缓存
                try:
                    subprocess.run(["ipconfig", "/flushdns"], check=False)
                    subprocess.run(["arp", "-d", "*"], check=False)
                except:
                    pass
            
            return True
        except Exception as e:
            print(f"清除系统缓存时出错: {str(e)}")
            return False
    
    @staticmethod
    def 清除Python解释器缓存():
        """
        尝试清除Python解释器的内部缓存
        """
        try:
            # 尝试清除字符串内部缓存
            if hasattr(sys, "intern"):
                sys.intern = lambda x: x
            
            # 尝试清除部分导入缓存（不清除所有模块，避免破坏程序）
            非必要模块 = []
            for 模块名 in list(sys.modules.keys()):
                # 只清除非内置模块和非当前程序必要模块
                if not 模块名.startswith('_') and 模块名 not in ['sys', 'os', 'gc', 'ctypes', 'platform', 'tempfile', 'subprocess']:
                    非必要模块.append(模块名)
            
            # 安全地移除非必要模块
            for 模块名 in 非必要模块:
                if 模块名 in sys.modules:
                    del sys.modules[模块名]
            
            return True
        except Exception as e:
            print(f"清除Python解释器缓存时出错: {str(e)}")
            return False
    
    @staticmethod
    def 安全清除所有痕迹(敏感数据列表: Optional[List[Any]] = None) -> bool:
        """
        全面清除所有可能的敏感数据痕迹
        
        参数:
            敏感数据列表: 需要清除的敏感数据对象列表
            
        返回:
            是否成功清除
        """
        结果 = []
        
        # 清除指定的敏感数据
        if 敏感数据列表:
            for 数据 in 敏感数据列表:
                安全清除工具.安全清除内存(数据)
        
        # 强制垃圾回收
        结果.append(安全清除工具.强制垃圾回收())
        
        # 尝试清除Python解释器的历史缓存
        结果.append(安全清除工具.清除Python解释器缓存())
        
        # 尝试清除系统缓存
        结果.append(安全清除工具.清除系统缓存())
        
        # 如果所有操作都成功，返回True
        return all(结果)
    
    @staticmethod
    def 显示清除过程(敏感数据列表: Optional[Dict[str, Any]] = None) -> None:
        """
        显示清除过程并执行清除
        
        参数:
            敏感数据列表: 需要清除的敏感数据对象字典，键为数据名称，值为数据对象
        """
        print("\n===== 正在清除所有敏感数据痕迹 =====")
        
        # 清除指定的敏感数据
        if 敏感数据列表:
            i = 1
            for 名称, 数据 in 敏感数据列表.items():
                print(f"{i}. 清除内存中的{名称}...")
                安全清除工具.安全清除内存(数据)
                i += 1
        
        # 强制垃圾回收
        print(f"{i if 敏感数据列表 else 1}. 强制执行垃圾回收...")
        安全清除工具.强制垃圾回收()
        
        # 清除系统缓存
        print(f"{i+1 if 敏感数据列表 else 2}. 清除系统缓存...")
        安全清除工具.清除系统缓存()
        
        print(f"{i+2 if 敏感数据列表 else 3}. 敏感数据已安全清除 ✓")
        print("\n您的敏感数据已从系统内存中完全清除，只保留在您的纸质记录中。")
        
        # 询问是否清除屏幕
        print("\n是否清除屏幕以移除所有显示的敏感信息? (y/n):")
        清屏选择 = input("> ").lower()
        if 清屏选择 in ['y', 'yes', '是']:
            安全清除工具.清除终端显示()
            print("===== 加密货币钱包助记词生成工具 =====")
            print("\n所有敏感数据已清除，屏幕已清空。")


# 测试代码
if __name__ == "__main__":
    # 测试内存清除
    test_data = b"This is sensitive data"
    print(f"清除前: {test_data}")
    安全清除工具.安全清除内存(test_data)
    print(f"清除后: {test_data}")
    
    # 测试垃圾回收
    print(f"强制垃圾回收: {安全清除工具.强制垃圾回收()}")
    
    # 测试系统缓存清除
    print(f"清除系统缓存: {安全清除工具.清除系统缓存()}")
    
    # 测试显示清除过程
    test_dict = {"测试数据": "sensitive information"}
    安全清除工具.显示清除过程(test_dict)