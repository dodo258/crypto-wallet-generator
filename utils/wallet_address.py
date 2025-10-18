#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
钱包地址生成工具
从助记词或种子生成常见加密货币的钱包地址
"""

import hashlib
import hmac
import binascii
from typing import Dict, List, Tuple, Optional, Union

try:
    import base58
    import bech32
    import ecdsa
    from hdwallet import HDWallet
    from hdwallet.symbols import BTC, ETH, DOGE, LTC, BCH
    HDWALLET_AVAILABLE = True
except ImportError:
    HDWALLET_AVAILABLE = False


class 钱包地址生成器:
    """钱包地址生成器类，用于从助记词或种子生成加密货币地址"""
    
    @staticmethod
    def 检查依赖() -> bool:
        """
        检查是否安装了必要的依赖库
        
        返回:
            是否可用
        """
        return HDWALLET_AVAILABLE
    
    @staticmethod
    def 安装依赖提示() -> str:
        """
        返回安装依赖的提示信息
        
        返回:
            安装提示字符串
        """
        return "请安装必要的依赖库以启用钱包地址生成功能：\npip install hdwallet base58 bech32 ecdsa"
    
    @staticmethod
    def 从种子生成地址(种子: bytes, 币种: str = "BTC", 账户索引: int = 0, 地址索引: int = 0) -> Dict:
        """
        从种子生成指定币种的钱包地址
        
        参数:
            种子: 种子字节
            币种: 币种代码 (BTC, ETH, DOGE, LTC, BCH等)
            账户索引: HD钱包的账户索引
            地址索引: HD钱包的地址索引
            
        返回:
            包含地址信息的字典
        """
        if not HDWALLET_AVAILABLE:
            return {"错误": f"缺少必要的依赖库。{钱包地址生成器.安装依赖提示()}"}
        
        try:
            # 创建HD钱包
            hdwallet = HDWallet(symbol=币种)
            
            # 从种子导入
            hdwallet.from_seed(seed=种子)
            
            # 设置HD路径
            # m/44'/{币种索引}'/0'/0/0
            hdwallet.from_path(f"m/44'/{hdwallet.cryptocurrency().INDEX}'/{账户索引}'/0/{地址索引}")
            
            # 获取钱包信息
            钱包信息 = {
                "币种": 币种,
                "地址": hdwallet.address(),
                "公钥": hdwallet.public_key(),
                "HD路径": hdwallet.path(),
                "扩展公钥": hdwallet.extended_public_key(),
                "账户索引": 账户索引,
                "地址索引": 地址索引
            }
            
            return 钱包信息
        except Exception as e:
            return {"错误": f"生成{币种}地址时出错: {str(e)}"}
    
    @staticmethod
    def 从助记词生成地址(助记词: str, 密码短语: str = "", 币种: str = "BTC", 账户索引: int = 0, 地址索引: int = 0) -> Dict:
        """
        从助记词生成指定币种的钱包地址
        
        参数:
            助记词: 助记词字符串
            密码短语: 可选密码短语
            币种: 币种代码 (BTC, ETH, DOGE, LTC, BCH等)
            账户索引: HD钱包的账户索引
            地址索引: HD钱包的地址索引
            
        返回:
            包含地址信息的字典
        """
        if not HDWALLET_AVAILABLE:
            return {"错误": f"缺少必要的依赖库。{钱包地址生成器.安装依赖提示()}"}
        
        try:
            # 创建HD钱包
            hdwallet = HDWallet(symbol=币种)
            
            # 从助记词导入
            hdwallet.from_mnemonic(mnemonic=助记词, passphrase=密码短语)
            
            # 设置HD路径
            # m/44'/{币种索引}'/0'/0/0
            hdwallet.from_path(f"m/44'/{hdwallet.cryptocurrency().INDEX}'/{账户索引}'/0/{地址索引}")
            
            # 获取钱包信息
            钱包信息 = {
                "币种": 币种,
                "地址": hdwallet.address(),
                "公钥": hdwallet.public_key(),
                "HD路径": hdwallet.path(),
                "扩展公钥": hdwallet.extended_public_key(),
                "账户索引": 账户索引,
                "地址索引": 地址索引
            }
            
            return 钱包信息
        except Exception as e:
            return {"错误": f"生成{币种}地址时出错: {str(e)}"}
    
    @staticmethod
    def 生成多币种地址(助记词: str, 密码短语: str = "") -> Dict[str, Dict]:
        """
        从助记词生成多种常见加密货币的地址
        
        参数:
            助记词: 助记词字符串
            密码短语: 可选密码短语
            
        返回:
            包含多种币种地址信息的字典
        """
        if not HDWALLET_AVAILABLE:
            return {"错误": f"缺少必要的依赖库。{钱包地址生成器.安装依赖提示()}"}
        
        支持币种 = [BTC, ETH, DOGE, LTC, BCH]
        结果 = {}
        
        for 币种 in 支持币种:
            结果[币种] = 钱包地址生成器.从助记词生成地址(助记词, 密码短语, 币种)
        
        return 结果
    
    @staticmethod
    def 格式化地址信息(地址信息: Dict) -> str:
        """
        格式化地址信息为可读字符串
        
        参数:
            地址信息: 地址信息字典
            
        返回:
            格式化的字符串
        """
        if "错误" in 地址信息:
            return f"错误: {地址信息['错误']}"
        
        输出 = f"\n===== {地址信息['币种']}钱包地址 =====\n"
        输出 += f"地址: {地址信息['地址']}\n"
        输出 += f"HD路径: {地址信息['HD路径']}\n"
        输出 += f"公钥: {地址信息['公钥'][:10]}...{地址信息['公钥'][-10:]}\n"
        
        return 输出
    
    @staticmethod
    def 显示地址安全提示() -> str:
        """
        返回关于钱包地址安全性的提示
        
        返回:
            安全提示字符串
        """
        return """
===== 钱包地址安全提示 =====

1. 钱包地址是公开信息，可以安全分享给他人用于接收资金
2. 公钥和扩展公钥应当谨慎分享，特别是扩展公钥可能导致隐私泄露
3. 永远不要分享您的助记词、私钥或种子，这些信息可以控制您的资产
4. 在使用新生成的地址前，建议先发送小额资金测试
5. 不同币种的地址格式不同，请确保使用正确的地址格式
6. 考虑使用硬件钱包来增强安全性
"""


# 测试代码
if __name__ == "__main__":
    if 钱包地址生成器.检查依赖():
        测试助记词 = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"
        地址信息 = 钱包地址生成器.从助记词生成地址(测试助记词)
        print(钱包地址生成器.格式化地址信息(地址信息))
        print(钱包地址生成器.显示地址安全提示())
    else:
        print(钱包地址生成器.安装依赖提示())