#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
钱包地址生成测试
测试从助记词或种子生成加密货币地址的功能
"""

import unittest
import sys
import os
import re

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from utils.wallet_address import 钱包地址生成器
    WALLET_ADDRESS_AVAILABLE = True
except ImportError:
    WALLET_ADDRESS_AVAILABLE = False


@unittest.skipIf(not WALLET_ADDRESS_AVAILABLE, "钱包地址生成器不可用，跳过测试")
class 钱包地址测试(unittest.TestCase):
    """钱包地址生成功能的测试"""
    
    def setUp(self):
        """测试前的准备工作"""
        # 使用BIP-39测试向量中的助记词
        self.测试助记词 = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"
        self.测试密码短语 = ""
    
    def test_比特币地址生成(self):
        """测试比特币地址生成"""
        地址信息 = 钱包地址生成器.从助记词生成地址(self.测试助记词, self.测试密码短语, "BTC")
        
        # 检查地址是否存在
        self.assertIn("地址", 地址信息)
        
        # 检查比特币地址格式
        比特币地址 = 地址信息["地址"]
        self.assertTrue(比特币地址.startswith("1") or 比特币地址.startswith("3") or 比特币地址.startswith("bc1"))
        
        # 检查HD路径
        self.assertIn("HD路径", 地址信息)
        self.assertTrue(地址信息["HD路径"].startswith("m/44'/0'/"))
    
    def test_以太坊地址生成(self):
        """测试以太坊地址生成"""
        地址信息 = 钱包地址生成器.从助记词生成地址(self.测试助记词, self.测试密码短语, "ETH")
        
        # 检查地址是否存在
        self.assertIn("地址", 地址信息)
        
        # 检查以太坊地址格式
        以太坊地址 = 地址信息["地址"]
        self.assertTrue(以太坊地址.startswith("0x"))
        self.assertEqual(len(以太坊地址), 42)  # 0x + 40个十六进制字符
        
        # 检查HD路径
        self.assertIn("HD路径", 地址信息)
        self.assertTrue(地址信息["HD路径"].startswith("m/44'/60'/"))
    
    def test_多币种地址生成(self):
        """测试多币种地址生成"""
        地址信息字典 = 钱包地址生成器.生成多币种地址(self.测试助记词, self.测试密码短语)
        
        # 检查是否包含多种币种
        self.assertIn("BTC", 地址信息字典)
        self.assertIn("ETH", 地址信息字典)
        
        # 检查每种币种的地址格式
        for 币种, 地址信息 in 地址信息字典.items():
            self.assertIn("地址", 地址信息)
            self.assertIn("HD路径", 地址信息)
    
    def test_不同账户索引(self):
        """测试不同账户索引生成的地址"""
        地址信息1 = 钱包地址生成器.从助记词生成地址(self.测试助记词, self.测试密码短语, "BTC", 账户索引=0)
        地址信息2 = 钱包地址生成器.从助记词生成地址(self.测试助记词, self.测试密码短语, "BTC", 账户索引=1)
        
        # 不同账户索引应该生成不同的地址
        self.assertNotEqual(地址信息1["地址"], 地址信息2["地址"])
    
    def test_不同地址索引(self):
        """测试不同地址索引生成的地址"""
        地址信息1 = 钱包地址生成器.从助记词生成地址(self.测试助记词, self.测试密码短语, "BTC", 账户索引=0, 地址索引=0)
        地址信息2 = 钱包地址生成器.从助记词生成地址(self.测试助记词, self.测试密码短语, "BTC", 账户索引=0, 地址索引=1)
        
        # 不同地址索引应该生成不同的地址
        self.assertNotEqual(地址信息1["地址"], 地址信息2["地址"])
    
    def test_格式化输出(self):
        """测试格式化输出功能"""
        地址信息 = 钱包地址生成器.从助记词生成地址(self.测试助记词, self.测试密码短语, "BTC")
        格式化输出 = 钱包地址生成器.格式化地址信息(地址信息)
        
        # 检查格式化输出是否包含关键信息
        self.assertIn("BTC钱包地址", 格式化输出)
        self.assertIn("地址:", 格式化输出)
        self.assertIn("HD路径:", 格式化输出)
    
    def test_安全提示(self):
        """测试安全提示功能"""
        安全提示 = 钱包地址生成器.显示地址安全提示()
        
        # 检查安全提示是否包含关键信息
        self.assertIn("钱包地址安全提示", 安全提示)
        self.assertIn("钱包地址是公开信息", 安全提示)


if __name__ == "__main__":
    unittest.main()