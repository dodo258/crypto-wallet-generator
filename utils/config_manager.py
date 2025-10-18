#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
配置文件管理工具
用于管理钱包生成工具的配置选项
"""

import os
import json
import time
from typing import Dict, Any, Optional
from pathlib import Path


class 配置管理器:
    """配置管理器类，用于管理和持久化配置选项"""
    
    # 默认配置
    默认配置 = {
        "版本": "1.0.0",
        "语言": "chinese_simplified",
        "默认助记词语言": "english",
        "默认助记词长度": 256,  # 位数，对应24个词
        "使用真随机": True,
        "熵源要求数量": 3,
        "自动检查更新": True,
        "显示安全提示": True,
        "备份提醒间隔天数": 90,
        "上次备份检查时间": 0,
        "界面": {
            "颜色主题": "暗色",
            "字体大小": "中",
        },
        "高级选项": {
            "允许伪随机": False,
            "允许导出私钥": False,
            "允许导出种子": True,
            "允许生成二维码": True,
            "允许生成钱包地址": True,
            "密码强度最低要求": 40,  # 0-100分
        },
        "路径": {
            "默认导出目录": "",
            "二维码保存目录": "",
        }
    }
    
    def __init__(self, 配置文件路径: Optional[str] = None):
        """
        初始化配置管理器
        
        参数:
            配置文件路径: 配置文件的路径，如果为None则使用默认路径
        """
        if 配置文件路径 is None:
            # 使用用户主目录下的.crypto_wallet目录
            主目录 = str(Path.home())
            配置目录 = os.path.join(主目录, ".crypto_wallet")
            
            # 确保配置目录存在
            os.makedirs(配置目录, exist_ok=True)
            
            self.配置文件路径 = os.path.join(配置目录, "config.json")
        else:
            self.配置文件路径 = 配置文件路径
        
        # 加载配置
        self.配置 = self.加载配置()
    
    def 加载配置(self) -> Dict[str, Any]:
        """
        从文件加载配置，如果文件不存在则使用默认配置
        
        返回:
            配置字典
        """
        if os.path.exists(self.配置文件路径):
            try:
                with open(self.配置文件路径, 'r', encoding='utf-8') as f:
                    配置 = json.load(f)
                
                # 合并默认配置和加载的配置，确保所有必要的键都存在
                合并配置 = self.默认配置.copy()
                self._递归更新字典(合并配置, 配置)
                
                return 合并配置
            except Exception as e:
                print(f"加载配置文件时出错: {str(e)}")
                print("将使用默认配置")
                return self.默认配置.copy()
        else:
            # 如果配置文件不存在，使用默认配置并保存
            self.保存配置(self.默认配置)
            return self.默认配置.copy()
    
    def 保存配置(self, 配置: Dict[str, Any] = None) -> bool:
        """
        保存配置到文件
        
        参数:
            配置: 要保存的配置字典，如果为None则使用当前配置
            
        返回:
            是否成功保存
        """
        if 配置 is None:
            配置 = self.配置
        
        try:
            with open(self.配置文件路径, 'w', encoding='utf-8') as f:
                json.dump(配置, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存配置文件时出错: {str(e)}")
            return False
    
    def 获取配置(self, 键: str, 默认值: Any = None) -> Any:
        """
        获取配置项的值
        
        参数:
            键: 配置项的键，可以使用点号分隔的路径，如"高级选项.允许导出私钥"
            默认值: 如果键不存在，返回的默认值
            
        返回:
            配置项的值
        """
        # 处理嵌套键
        键路径 = 键.split('.')
        当前值 = self.配置
        
        try:
            for 部分 in 键路径:
                当前值 = 当前值[部分]
            return 当前值
        except (KeyError, TypeError):
            return 默认值
    
    def 设置配置(self, 键: str, 值: Any) -> bool:
        """
        设置配置项的值
        
        参数:
            键: 配置项的键，可以使用点号分隔的路径，如"高级选项.允许导出私钥"
            值: 要设置的值
            
        返回:
            是否成功设置
        """
        # 处理嵌套键
        键路径 = 键.split('.')
        当前字典 = self.配置
        
        # 遍历路径，直到最后一个键
        for i, 部分 in enumerate(键路径[:-1]):
            if 部分 not in 当前字典:
                当前字典[部分] = {}
            elif not isinstance(当前字典[部分], dict):
                当前字典[部分] = {}
            
            当前字典 = 当前字典[部分]
        
        # 设置最后一个键的值
        当前字典[键路径[-1]] = 值
        
        # 保存配置
        return self.保存配置()
    
    def 重置配置(self) -> bool:
        """
        重置配置为默认值
        
        返回:
            是否成功重置
        """
        self.配置 = self.默认配置.copy()
        return self.保存配置()
    
    def 显示配置(self) -> str:
        """
        格式化显示当前配置
        
        返回:
            格式化的配置字符串
        """
        return json.dumps(self.配置, ensure_ascii=False, indent=2)
    
    def 检查备份提醒(self) -> bool:
        """
        检查是否需要提醒用户备份
        
        返回:
            是否需要提醒
        """
        # 获取上次备份检查时间和备份提醒间隔
        上次备份检查时间 = self.获取配置("上次备份检查时间", 0)
        备份提醒间隔天数 = self.获取配置("备份提醒间隔天数", 90)
        
        # 计算当前时间和上次备份检查时间的差值（天数）
        当前时间 = time.time()
        经过天数 = (当前时间 - 上次备份检查时间) / (24 * 60 * 60)
        
        # 如果经过的天数大于等于备份提醒间隔天数，需要提醒
        if 经过天数 >= 备份提醒间隔天数:
            # 更新上次备份检查时间
            self.设置配置("上次备份检查时间", 当前时间)
            return True
        
        return False
    
    def 更新备份检查时间(self) -> None:
        """更新上次备份检查时间为当前时间"""
        self.设置配置("上次备份检查时间", time.time())
    
    def _递归更新字典(self, 目标: Dict, 源: Dict) -> None:
        """
        递归更新字典，保留目标字典中的键
        
        参数:
            目标: 要更新的目标字典
            源: 源字典
        """
        for 键, 值 in 源.items():
            if 键 in 目标 and isinstance(目标[键], dict) and isinstance(值, dict):
                self._递归更新字典(目标[键], 值)
            else:
                目标[键] = 值


# 测试代码
if __name__ == "__main__":
    # 使用临时配置文件进行测试
    测试配置路径 = "test_config.json"
    
    # 创建配置管理器
    配置管理器 = 配置管理器(测试配置路径)
    
    # 显示默认配置
    print("默认配置:")
    print(配置管理器.显示配置())
    
    # 修改配置
    配置管理器.设置配置("语言", "english")
    配置管理器.设置配置("高级选项.允许导出私钥", True)
    配置管理器.设置配置("路径.默认导出目录", "/tmp/export")
    
    # 显示修改后的配置
    print("\n修改后的配置:")
    print(配置管理器.显示配置())
    
    # 获取配置项
    print("\n获取配置项:")
    print(f"语言: {配置管理器.获取配置('语言')}")
    print(f"允许导出私钥: {配置管理器.获取配置('高级选项.允许导出私钥')}")
    print(f"不存在的配置项: {配置管理器.获取配置('不存在的键', '默认值')}")
    
    # 清理测试文件
    if os.path.exists(测试配置路径):
        os.remove(测试配置路径)