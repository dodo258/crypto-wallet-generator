#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
二维码生成测试
测试助记词和种子的二维码生成功能
"""

import unittest
import sys
import os
import tempfile
import base64

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from utils.qrcode_generator import 二维码生成器
    QRCODE_AVAILABLE = True
except ImportError:
    QRCODE_AVAILABLE = False


@unittest.skipIf(not QRCODE_AVAILABLE, "二维码生成器不可用，跳过测试")
class 二维码测试(unittest.TestCase):
    """二维码生成功能的测试"""
    
    def setUp(self):
        """测试前的准备工作"""
        # 使用BIP-39测试向量中的助记词
        self.测试助记词 = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"
        self.测试种子 = bytes.fromhex("5eb00bbddcf069084889a8ab9155568165f5c453ccb85e70811aaed6f6da5fc19a5ac40b389cd370d086206dec8aa6c43daea6690f20ad3d8d48b2d2ce9e38e4")
    
    def tearDown(self):
        """测试后的清理工作"""
        # 删除测试过程中创建的临时文件
        for 文件名 in os.listdir():
            if 文件名.startswith("test_qrcode_") and 文件名.endswith(".png"):
                try:
                    os.remove(文件名)
                except:
                    pass
    
    def test_依赖检查(self):
        """测试依赖检查功能"""
        # 检查依赖是否可用
        依赖可用 = 二维码生成器.检查依赖()
        
        # 如果依赖不可用，应该提供安装提示
        if not 依赖可用:
            安装提示 = 二维码生成器.安装依赖提示()
            self.assertIn("pip install", 安装提示)
        else:
            # 如果依赖可用，继续测试
            self.assertTrue(依赖可用)
    
    @unittest.skipIf(not QRCODE_AVAILABLE, "二维码生成器依赖不可用，跳过测试")
    def test_生成二维码(self):
        """测试生成二维码功能"""
        # 生成临时文件路径
        临时文件路径 = "test_qrcode_general.png"
        
        # 生成二维码
        结果 = 二维码生成器.生成二维码("测试数据", 临时文件路径)
        
        # 检查结果是否为文件路径
        self.assertEqual(结果, 临时文件路径)
        
        # 检查文件是否存在
        self.assertTrue(os.path.exists(临时文件路径))
        
        # 检查文件大小是否合理
        self.assertGreater(os.path.getsize(临时文件路径), 100)
    
    @unittest.skipIf(not QRCODE_AVAILABLE, "二维码生成器依赖不可用，跳过测试")
    def test_生成助记词二维码(self):
        """测试生成助记词二维码功能"""
        # 生成临时文件路径
        临时文件路径 = "test_qrcode_mnemonic.png"
        
        # 生成助记词二维码
        结果 = 二维码生成器.生成助记词二维码(self.测试助记词, 临时文件路径)
        
        # 检查结果是否为文件路径
        self.assertEqual(结果, 临时文件路径)
        
        # 检查文件是否存在
        self.assertTrue(os.path.exists(临时文件路径))
        
        # 检查文件大小是否合理
        self.assertGreater(os.path.getsize(临时文件路径), 100)
    
    @unittest.skipIf(not QRCODE_AVAILABLE, "二维码生成器依赖不可用，跳过测试")
    def test_生成种子二维码(self):
        """测试生成种子二维码功能"""
        # 生成临时文件路径
        临时文件路径 = "test_qrcode_seed.png"
        
        # 生成种子二维码
        结果 = 二维码生成器.生成种子二维码(self.测试种子, 临时文件路径)
        
        # 检查结果是否为文件路径
        self.assertEqual(结果, 临时文件路径)
        
        # 检查文件是否存在
        self.assertTrue(os.path.exists(临时文件路径))
        
        # 检查文件大小是否合理
        self.assertGreater(os.path.getsize(临时文件路径), 100)
    
    @unittest.skipIf(not QRCODE_AVAILABLE, "二维码生成器依赖不可用，跳过测试")
    def test_不保存到文件(self):
        """测试不保存到文件的二维码生成功能"""
        # 生成二维码但不保存到文件
        结果 = 二维码生成器.生成二维码("测试数据", None)
        
        # 检查结果是否为base64编码的字符串
        self.assertIsInstance(结果, str)
        
        # 尝试解码base64
        try:
            解码结果 = base64.b64decode(结果)
            self.assertGreater(len(解码结果), 100)
        except:
            self.fail("结果不是有效的base64编码")
    
    @unittest.skipIf(not QRCODE_AVAILABLE, "二维码生成器依赖不可用，跳过测试")
    def test_样式化二维码(self):
        """测试样式化二维码生成功能"""
        # 生成临时文件路径
        普通文件路径 = "test_qrcode_normal.png"
        样式化文件路径 = "test_qrcode_styled.png"
        
        # 生成普通二维码
        二维码生成器.生成二维码("测试数据", 普通文件路径, 样式化=False)
        
        # 生成样式化二维码
        二维码生成器.生成二维码("测试数据", 样式化文件路径, 样式化=True)
        
        # 检查两个文件是否都存在
        self.assertTrue(os.path.exists(普通文件路径))
        self.assertTrue(os.path.exists(样式化文件路径))
        
        # 样式化二维码通常会更大一些
        普通大小 = os.path.getsize(普通文件路径)
        样式化大小 = os.path.getsize(样式化文件路径)
        
        # 注意：这个测试可能不总是成立，因为样式化不一定会导致文件更大
        # 所以我们只是检查两个文件是否不同
        self.assertNotEqual(普通大小, 样式化大小)
    
    def test_安全提示(self):
        """测试安全提示功能"""
        安全提示 = 二维码生成器.显示二维码安全提示()
        
        # 检查安全提示是否包含关键信息
        self.assertIn("二维码安全提示", 安全提示)
        self.assertIn("包含您的助记词或种子", 安全提示)


if __name__ == "__main__":
    unittest.main()