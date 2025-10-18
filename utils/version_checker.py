#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
版本检查工具
用于检查工具的最新版本并提供更新提示
"""

import os
import json
import time
import urllib.request
import urllib.error
import platform
import subprocess
from typing import Dict, Any, Optional, Tuple


class 版本检查器:
    """版本检查器类，用于检查工具的最新版本"""
    
    # 当前版本
    当前版本 = "1.1.0"
    
    # GitHub仓库信息
    仓库所有者 = "dodo258"
    仓库名称 = "crypto-wallet-generator"
    
    # 版本检查间隔（秒）
    检查间隔 = 86400  # 24小时
    
    # 版本缓存文件
    @staticmethod
    def 获取缓存文件路径() -> str:
        """获取版本缓存文件路径"""
        主目录 = os.path.expanduser("~")
        缓存目录 = os.path.join(主目录, ".crypto_wallet")
        os.makedirs(缓存目录, exist_ok=True)
        return os.path.join(缓存目录, "version_cache.json")
    
    @staticmethod
    def 获取最新版本() -> Dict[str, Any]:
        """
        从GitHub获取最新版本信息
        
        返回:
            包含版本信息的字典
        """
        try:
            # 构建API URL
            api_url = f"https://api.github.com/repos/{版本检查器.仓库所有者}/{版本检查器.仓库名称}/releases/latest"
            
            # 创建请求
            请求 = urllib.request.Request(api_url)
            请求.add_header("User-Agent", "CryptoWalletGenerator")
            
            # 发送请求
            with urllib.request.urlopen(请求, timeout=5) as 响应:
                数据 = json.loads(响应.read().decode("utf-8"))
            
            # 提取版本信息
            标签名 = 数据.get("tag_name", "").lstrip("v")
            发布名 = 数据.get("name", "")
            发布说明 = 数据.get("body", "")
            发布URL = 数据.get("html_url", "")
            
            return {
                "版本": 标签名,
                "名称": 发布名,
                "说明": 发布说明,
                "URL": 发布URL,
                "检查时间": time.time()
            }
        except (urllib.error.URLError, json.JSONDecodeError, KeyError) as e:
            print(f"获取最新版本信息时出错: {str(e)}")
            return {
                "版本": 版本检查器.当前版本,
                "名称": "未知",
                "说明": "",
                "URL": "",
                "检查时间": time.time(),
                "错误": str(e)
            }
    
    @staticmethod
    def 保存版本缓存(版本信息: Dict[str, Any]) -> None:
        """
        保存版本信息到缓存文件
        
        参数:
            版本信息: 要保存的版本信息
        """
        try:
            缓存文件路径 = 版本检查器.获取缓存文件路径()
            with open(缓存文件路径, "w", encoding="utf-8") as f:
                json.dump(版本信息, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存版本缓存时出错: {str(e)}")
    
    @staticmethod
    def 加载版本缓存() -> Dict[str, Any]:
        """
        从缓存文件加载版本信息
        
        返回:
            缓存的版本信息，如果缓存不存在或无效则返回空字典
        """
        try:
            缓存文件路径 = 版本检查器.获取缓存文件路径()
            if os.path.exists(缓存文件路径):
                with open(缓存文件路径, "r", encoding="utf-8") as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"加载版本缓存时出错: {str(e)}")
            return {}
    
    @staticmethod
    def 检查更新(强制检查: bool = False) -> Tuple[bool, Dict[str, Any]]:
        """
        检查是否有新版本可用
        
        参数:
            强制检查: 是否强制检查，忽略缓存
            
        返回:
            (是否有更新, 版本信息)
        """
        # 加载缓存
        缓存 = 版本检查器.加载版本缓存()
        当前时间 = time.time()
        
        # 如果缓存存在且未过期，且不是强制检查，则使用缓存
        if not 强制检查 and 缓存 and "检查时间" in 缓存 and 当前时间 - 缓存["检查时间"] < 版本检查器.检查间隔:
            最新版本信息 = 缓存
        else:
            # 否则获取最新版本信息
            最新版本信息 = 版本检查器.获取最新版本()
            # 保存到缓存
            版本检查器.保存版本缓存(最新版本信息)
        
        # 比较版本
        当前版本元组 = 版本检查器.解析版本号(版本检查器.当前版本)
        最新版本元组 = 版本检查器.解析版本号(最新版本信息.get("版本", "0.0.0"))
        
        有更新 = 最新版本元组 > 当前版本元组
        
        return 有更新, 最新版本信息
    
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
            return tuple(map(int, 版本号.split(".")))
        except:
            return (0, 0, 0)
    
    @staticmethod
    def 格式化更新提示(版本信息: Dict[str, Any]) -> str:
        """
        格式化更新提示信息
        
        参数:
            版本信息: 版本信息字典
            
        返回:
            格式化的更新提示
        """
        提示 = f"\n===== 发现新版本 {版本信息.get('版本', '未知')} =====\n"
        提示 += f"当前版本: {版本检查器.当前版本}\n"
        提示 += f"最新版本: {版本信息.get('版本', '未知')}\n"
        
        if 版本信息.get("名称"):
            提示 += f"版本名称: {版本信息['名称']}\n"
        
        if 版本信息.get("说明"):
            提示 += "\n更新说明:\n"
            for 行 in 版本信息["说明"].split("\n"):
                提示 += f"  {行}\n"
        
        if 版本信息.get("URL"):
            提示 += f"\n下载地址: {版本信息['URL']}\n"
        
        提示 += "\n更新方法:\n"
        提示 += "  1. 访问上述下载地址\n"
        提示 += "  2. 下载最新版本\n"
        提示 += "  3. 解压并替换当前文件\n"
        
        return 提示
    
    @staticmethod
    def 自动更新() -> Tuple[bool, str]:
        """
        尝试自动更新工具
        
        返回:
            (是否成功, 结果信息)
        """
        # 检查是否在Git仓库中
        if not os.path.exists(".git"):
            return False, "未检测到Git仓库，无法自动更新"
        
        try:
            # 检查Git是否可用
            subprocess.run(["git", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # 拉取最新代码
            结果 = subprocess.run(["git", "pull"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            输出 = 结果.stdout.decode("utf-8")
            
            if "Already up to date" in 输出:
                return True, "已经是最新版本"
            else:
                return True, f"更新成功:\n{输出}"
        except subprocess.CalledProcessError as e:
            return False, f"更新失败: {e.stderr.decode('utf-8')}"
        except Exception as e:
            return False, f"更新失败: {str(e)}"


# 测试代码
if __name__ == "__main__":
    print(f"当前版本: {版本检查器.当前版本}")
    
    有更新, 版本信息 = 版本检查器.检查更新(强制检查=True)
    
    if 有更新:
        print("发现新版本!")
        print(版本检查器.格式化更新提示(版本信息))
    else:
        print("已经是最新版本")
        
    # 尝试自动更新
    成功, 信息 = 版本检查器.自动更新()
    print(f"自动更新结果: {信息}")