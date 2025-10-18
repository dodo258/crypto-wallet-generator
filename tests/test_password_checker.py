#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
密码强度检查器测试
"""

import unittest
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from utils.password_checker import 密码强度检查器
except ImportError:
    print("无法导入密码强度检查器模块，请确保utils目录在Python路径中")
    sys.exit(1)


class 密码强度检查器测试(unittest.TestCase):
    """密码强度检查器的单元测试"""
    
    def test_空密码(self):
        """测试空密码"""
        结果 = 密码强度检查器.检查密码强度("")
        self.assertEqual(结果["分数"], 0)
        self.assertEqual(结果["强度"], "极弱")
        self.assertIn("密码不能为空", 结果["建议"])
    
    def test_弱密码(self):
        """测试弱密码"""
        弱密码列表 = ["password", "123456", "qwerty", "abc123"]
        for 密码 in 弱密码列表:
            结果 = 密码强度检查器.检查密码强度(密码)
            self.assertLess(结果["分数"], 40)
            self.assertIn(结果["强度"], ["极弱", "弱"])
    
    def test_强密码(self):
        """测试强密码"""
        强密码 = "P@ssw0rd!2023XYZ"
        结果 = 密码强度检查器.检查密码强度(强密码)
        self.assertGreaterEqual(结果["分数"], 60)
        self.assertIn(结果["强度"], ["中等", "强", "极强"])
    
    def test_重复模式检测(self):
        """测试重复模式检测"""
        重复密码 = "aaa123456"
        结果 = 密码强度检查器.检查密码强度(重复密码)
        self.assertTrue(结果["详情"]["重复模式"]["存在"])
        self.assertEqual(结果["详情"]["重复模式"]["模式"], "aaa")
    
    def test_序列模式检测(self):
        """测试序列模式检测"""
        序列密码 = "abcdef123"
        结果 = 密码强度检查器.检查密码强度(序列密码)
        self.assertTrue(结果["详情"]["序列模式"]["存在"])
    
    def test_复杂度检测(self):
        """测试复杂度检测"""
        复杂密码 = "Abc123!@#"
        结果 = 密码强度检查器.检查密码强度(复杂密码)
        self.assertTrue(结果["详情"]["复杂度"]["小写字母"])
        self.assertTrue(结果["详情"]["复杂度"]["大写字母"])
        self.assertTrue(结果["详情"]["复杂度"]["数字"])
        self.assertTrue(结果["详情"]["复杂度"]["特殊字符"])
    
    def test_长度检测(self):
        """测试长度检测"""
        短密码 = "abc123"
        长密码 = "abcdefghijklmnopqrstuvwxyz123456"
        
        短密码结果 = 密码强度检查器.检查密码强度(短密码)
        长密码结果 = 密码强度检查器.检查密码强度(长密码)
        
        self.assertLess(短密码结果["详情"]["长度"]["分数"], 长密码结果["详情"]["长度"]["分数"])
    
    def test_建议生成(self):
        """测试建议生成"""
        建议列表 = 密码强度检查器.生成密码建议()
        self.assertIsInstance(建议列表, list)
        self.assertGreater(len(建议列表), 0)
    
    def test_格式化输出(self):
        """测试格式化输出"""
        结果 = 密码强度检查器.检查密码强度("test123")
        输出 = 密码强度检查器.格式化输出密码强度(结果)
        self.assertIsInstance(输出, str)
        self.assertIn("强度:", 输出)
        self.assertIn("建议:", 输出)


if __name__ == "__main__":
    unittest.main()