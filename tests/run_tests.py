#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试运行脚本
运行所有单元测试并生成报告
"""

import unittest
import sys
import os
import time

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def 运行所有测试():
    """运行所有测试并返回测试结果"""
    # 发现所有测试
    测试加载器 = unittest.TestLoader()
    测试套件 = 测试加载器.discover(os.path.dirname(__file__), pattern="test_*.py")
    
    # 运行测试
    测试运行器 = unittest.TextTestRunner(verbosity=2)
    结果 = 测试运行器.run(测试套件)
    
    return 结果


def 生成测试报告(结果):
    """生成测试报告"""
    print("\n===== 测试报告 =====")
    print(f"运行测试: {结果.testsRun}")
    print(f"成功: {结果.testsRun - len(结果.failures) - len(结果.errors)}")
    print(f"失败: {len(结果.failures)}")
    print(f"错误: {len(结果.errors)}")
    
    if 结果.failures:
        print("\n----- 失败测试 -----")
        for 测试, 错误信息 in 结果.failures:
            print(f"\n{测试}")
            print(f"{错误信息}")
    
    if 结果.errors:
        print("\n----- 错误测试 -----")
        for 测试, 错误信息 in 结果.errors:
            print(f"\n{测试}")
            print(f"{错误信息}")
    
    if 结果.skipped:
        print("\n----- 跳过测试 -----")
        for 测试, 原因 in 结果.skipped:
            print(f"{测试}: {原因}")


def 检查依赖():
    """检查测试所需的依赖"""
    缺失依赖 = []
    
    # 检查基本依赖
    try:
        import mnemonic
    except ImportError:
        缺失依赖.append("mnemonic")
    
    try:
        import cryptography
    except ImportError:
        缺失依赖.append("cryptography")
    
    # 检查可选依赖
    try:
        import shamir_mnemonic
    except ImportError:
        print("警告: shamir_mnemonic 未安装，SLIP-39相关测试将被跳过")
    
    try:
        import qrcode
    except ImportError:
        print("警告: qrcode 未安装，二维码相关测试将被跳过")
    
    try:
        import hdwallet
    except ImportError:
        print("警告: hdwallet 未安装，钱包地址相关测试将被跳过")
    
    # 如果有缺失的基本依赖，提示安装
    if 缺失依赖:
        print("错误: 以下必要依赖未安装:")
        for 依赖 in 缺失依赖:
            print(f"  - {依赖}")
        print("\n请运行以下命令安装依赖:")
        print(f"pip install {' '.join(缺失依赖)}")
        return False
    
    return True


if __name__ == "__main__":
    print("===== 加密货币钱包助记词生成工具测试 =====\n")
    
    # 检查依赖
    if not 检查依赖():
        sys.exit(1)
    
    # 记录开始时间
    开始时间 = time.time()
    
    # 运行测试
    测试结果 = 运行所有测试()
    
    # 记录结束时间
    结束时间 = time.time()
    
    # 生成报告
    生成测试报告(测试结果)
    
    # 显示运行时间
    运行时间 = 结束时间 - 开始时间
    print(f"\n测试运行时间: {运行时间:.2f} 秒")
    
    # 返回适当的退出码
    if 测试结果.wasSuccessful():
        print("\n所有测试通过!")
        sys.exit(0)
    else:
        print("\n测试失败!")
        sys.exit(1)