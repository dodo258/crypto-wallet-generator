#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
熵源质量测试
测试熵源生成器的随机性质量
"""

import unittest
import sys
import os
import math
import statistics
from collections import Counter

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from crypto_wallet_secure_optimized import 熵源生成器, 熵池
except ImportError:
    print("无法导入熵源生成器模块，请确保项目根目录在Python路径中")
    sys.exit(1)


class 熵源质量测试(unittest.TestCase):
    """熵源生成器的质量测试"""
    
    def setUp(self):
        """测试前的准备工作"""
        self.熵源生成器 = 熵源生成器()
        self.样本大小 = 10000  # 用于统计测试的样本大小
    
    def test_熵池健康检查(self):
        """测试熵池健康检查功能"""
        # 创建一个新的熵池
        熵池实例 = 熵池()
        
        # 初始状态应该不健康
        self.assertFalse(熵池实例.熵池是否健康())
        
        # 添加一个熵源
        熵池实例.添加熵("测试熵源1", b"test entropy 1")
        self.assertFalse(熵池实例.熵池是否健康())  # 仍然不健康
        
        # 添加足够的熵源
        熵池实例.添加熵("测试熵源2", b"test entropy 2")
        熵池实例.添加熵("测试熵源3", b"test entropy 3")
        self.assertTrue(熵池实例.熵池是否健康())  # 现在应该健康了
    
    def test_熵源收集(self):
        """测试熵源收集功能"""
        # 收集所有可用熵源
        self.熵源生成器.收集所有可用熵(包含用户熵=False)  # 不包含用户熵，避免交互
        
        # 获取熵池状态
        熵池状态 = self.熵源生成器.获取熵池状态()
        
        # 检查是否收集了足够的熵源
        self.assertGreaterEqual(熵池状态["熵源数量"], 3)
        self.assertGreaterEqual(熵池状态["熵池健康度"], 100)
    
    def test_熵生成一致性(self):
        """测试熵生成的一致性"""
        # 收集熵源
        self.熵源生成器.收集所有可用熵(包含用户熵=False)
        
        # 生成两个相同大小的熵
        熵1 = self.熵源生成器.获取熵(32)
        熵2 = self.熵源生成器.获取熵(32)
        
        # 两个熵应该不同
        self.assertNotEqual(熵1, 熵2)
        
        # 长度应该正确
        self.assertEqual(len(熵1), 32)
        self.assertEqual(len(熵2), 32)
    
    def test_熵分布均匀性(self):
        """测试熵的分布均匀性"""
        # 收集熵源
        self.熵源生成器.收集所有可用熵(包含用户熵=False)
        
        # 生成大量随机字节
        随机字节 = self.熵源生成器.获取熵(self.样本大小)
        
        # 统计每个字节值的出现次数
        计数器 = Counter(随机字节)
        
        # 计算卡方统计量
        期望频率 = self.样本大小 / 256  # 每个字节值的期望出现次数
        卡方值 = sum((计数器[i] - 期望频率) ** 2 / 期望频率 for i in range(256) if i in 计数器)
        
        # 对于255个自由度，95%置信水平的卡方临界值约为293.25
        # 如果卡方值小于临界值，则分布可以认为是均匀的
        self.assertLess(卡方值, 293.25)
    
    def test_熵比特相关性(self):
        """测试熵的比特之间的相关性"""
        # 收集熵源
        self.熵源生成器.收集所有可用熵(包含用户熵=False)
        
        # 生成大量随机字节
        随机字节 = self.熵源生成器.获取熵(self.样本大小)
        
        # 将字节转换为比特序列
        比特序列 = []
        for 字节 in 随机字节:
            for i in range(8):
                比特序列.append((字节 >> i) & 1)
        
        # 计算相邻比特的相关性
        相关性 = 0
        for i in range(len(比特序列) - 1):
            相关性 += (2 * 比特序列[i] - 1) * (2 * 比特序列[i + 1] - 1)
        相关性 /= (len(比特序列) - 1)
        
        # 相关性应该接近0
        self.assertAlmostEqual(相关性, 0, delta=0.05)
    
    def test_熵信息熵(self):
        """测试熵的信息熵"""
        # 收集熵源
        self.熵源生成器.收集所有可用熵(包含用户熵=False)
        
        # 生成大量随机字节
        随机字节 = self.熵源生成器.获取熵(self.样本大小)
        
        # 统计每个字节值的出现次数
        计数器 = Counter(随机字节)
        
        # 计算信息熵
        总数 = len(随机字节)
        信息熵 = 0
        for 计数 in 计数器.values():
            概率 = 计数 / 总数
            信息熵 -= 概率 * math.log2(概率)
        
        # 理想情况下，256个可能的字节值的均匀分布的信息熵为8比特
        # 允许有一定的误差
        self.assertGreaterEqual(信息熵, 7.9)
    
    def test_系统熵源(self):
        """测试系统熵源"""
        # 测试系统熵源
        系统熵 = 熵源生成器.获取系统熵(32)
        self.assertEqual(len(系统熵), 32)
        
        # 两次调用应该返回不同的结果
        系统熵2 = 熵源生成器.获取系统熵(32)
        self.assertNotEqual(系统熵, 系统熵2)
    
    def test_混合熵源(self):
        """测试混合熵源"""
        # 测试混合熵源
        混合熵 = 熵源生成器.获取混合熵(32)
        self.assertEqual(len(混合熵), 32)
        
        # 两次调用应该返回不同的结果
        混合熵2 = 熵源生成器.获取混合熵(32)
        self.assertNotEqual(混合熵, 混合熵2)


if __name__ == "__main__":
    unittest.main()