#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
加密货币钱包助记词生成工具（中文版）
支持真随机和伪随机两种模式生成符合BIP39标准的英文助记词
"""

import os
import sys
import hashlib
import random
import time
from typing import List, Optional
from mnemonic import Mnemonic
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes

class 熵源生成器:
    """熵源生成器基类"""
    
    @staticmethod
    def 获取系统熵(字节数: int) -> bytes:
        """
        从操作系统获取真随机熵
        
        参数:
            字节数: 需要的字节数
            
        返回:
            随机字节
        """
        try:
            return os.urandom(字节数)
        except NotImplementedError:
            raise RuntimeError("当前系统不支持os.urandom，无法获取系统随机熵")
    
    @staticmethod
    def 获取混合熵(字节数: int) -> bytes:
        """
        混合多种熵源获取更高质量的随机性
        
        参数:
            字节数: 需要的字节数
            
        返回:
            随机字节
        """
        # 系统熵
        系统熵 = 熵源生成器.获取系统熵(字节数)
        
        # 创建一个哈希对象来混合熵源
        哈希器 = hashlib.sha512()
        
        # 添加系统熵
        哈希器.update(系统熵)
        
        # 添加当前时间微秒级精度
        哈希器.update(str(time.time()).encode())
        
        # 如果可能，添加硬件随机性
        try:
            # 尝试读取/dev/random (仅在类Unix系统上可用)
            if os.path.exists('/dev/random'):
                with open('/dev/random', 'rb') as f:
                    哈希器.update(f.read(32))
        except:
            pass
        
        # 生成一些计算随机性
        私钥 = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        哈希器.update(str(id(私钥)).encode())
        
        # 获取最终哈希
        最终哈希 = 哈希器.digest()
        
        # 确保返回正确的字节数
        return 最终哈希[:字节数]
    
    @staticmethod
    def 获取伪随机熵(字节数: int) -> bytes:
        """
        使用Python的伪随机数生成器生成熵
        
        参数:
            字节数: 需要的字节数
            
        返回:
            随机字节
        """
        # 使用当前时间作为种子
        random.seed(time.time())
        
        # 生成随机字节
        随机字节列表 = [random.randint(0, 255) for _ in range(字节数)]
        
        # 转换为字节
        return bytes(随机字节列表)


class 钱包生成器:
    """钱包助记词生成器"""
    
    def __init__(self):
        """
        初始化钱包生成器，只使用英文助记词
        """
        self.语言 = "english"
        self.助记词工具 = Mnemonic(self.语言)
    
    def 生成助记词(self, 强度: int = 128, 使用真随机: bool = True) -> str:
        """
        生成助记词
        
        参数:
            强度: 熵的位数，必须是32的倍数，范围是128-256
                 128位生成12个词，256位生成24个词
            使用真随机: 是否使用真随机熵源
        
        返回:
            助记词字符串
        """
        if 强度 % 32 != 0 or 强度 < 128 or 强度 > 256:
            raise ValueError("熵的位数必须是32的倍数，范围是128-256")
        
        # 计算需要的字节数
        字节数 = 强度 // 8
        
        # 根据选择获取熵源
        if 使用真随机:
            熵 = 熵源生成器.获取混合熵(字节数)
        else:
            熵 = 熵源生成器.获取伪随机熵(字节数)
        
        # 生成助记词
        return self.助记词工具.to_mnemonic(熵)
    
    def 验证助记词(self, 助记词: str) -> bool:
        """
        验证助记词是否有效
        
        参数:
            助记词: 助记词字符串
            
        返回:
            是否有效
        """
        return self.助记词工具.check(助记词)
    
    def 助记词转种子(self, 助记词: str, 密码: str = "") -> bytes:
        """
        将助记词转换为种子
        
        参数:
            助记词: 助记词字符串
            密码: 可选密码短语
            
        返回:
            种子字节
        """
        种子 = self.助记词工具.to_seed(助记词, 密码)
        return 种子


def 显示菜单():
    """显示主菜单"""
    print("\n===== 加密货币钱包助记词生成工具 =====\n")
    print("1. 生成新的钱包助记词")
    print("2. 验证助记词是否有效")
    print("3. 退出程序")
    
    选择 = input("\n请输入选项 (1-3): ")
    return 选择


def 选择随机模式() -> bool:
    """选择随机模式"""
    print("\n===== 选择随机模式 =====\n")
    print("1. 真随机 (推荐，使用多种熵源混合生成高质量随机数)")
    print("   - 使用操作系统提供的真随机熵源")
    print("   - 混合多种熵源以增强随机性")
    print("   - 更安全，适合生成实际使用的钱包")
    print("\n2. 伪随机 (使用Python的随机数生成器)")
    print("   - 使用Python的伪随机数生成器")
    print("   - 速度更快，但安全性较低")
    print("   - 仅适合测试用途，不建议用于实际钱包")
    
    while True:
        选择 = input("\n请输入选项 (1-2): ")
        if 选择 == "1":
            return True
        elif 选择 == "2":
            return False
        else:
            print("无效选择，请重新输入")


def 选择助记词长度() -> int:
    """选择助记词长度"""
    print("\n===== 选择助记词长度 =====\n")
    print("1. 12个词 (128位熵，安全性适中)")
    print("2. 15个词 (160位熵)")
    print("3. 18个词 (192位熵)")
    print("4. 21个词 (224位熵)")
    print("5. 24个词 (256位熵，最高安全性)")
    
    长度映射 = {
        "1": 128,
        "2": 160,
        "3": 192,
        "4": 224,
        "5": 256
    }
    
    while True:
        选择 = input("\n请输入选项 (1-5): ")
        if 选择 in 长度映射:
            return 长度映射[选择]
        else:
            print("无效选择，请重新输入")


def 生成新钱包():
    """生成新的钱包助记词"""
    # 显示安全提示
    显示安全提示()
    
    # 选择随机模式
    使用真随机 = 选择随机模式()
    
    # 选择助记词长度
    强度 = 选择助记词长度()
    
    try:
        生成器 = 钱包生成器()
        助记词 = 生成器.生成助记词(强度, 使用真随机)
        
        print("\n===== 生成的助记词 =====\n")
        print(f"{助记词}\n")
        print(f"语言: english (英文)")
        print(f"词数: {len(助记词.split())}")
        print(f"随机模式: {'真随机' if 使用真随机 else '伪随机'}")
        
        # 显示重要提示
        print("\n⚠️ 重要提示：本程序不会在本地或云端保存您的助记词")
        print("⚠️ 请立即使用笔和纸记录下您的助记词，并保存在安全的地方")
        print("⚠️ 记录完成后，请使用验证功能确认您的记录是否正确")
        print("\n警告: 请将助记词安全保存，任何人获取到助记词将可以控制您的加密资产！")
        
        # 确认用户已记录助记词
        print("\n请确认您已安全抄写并保存了助记词")
        确认 = input("输入 'YES' 确认: ")
        
        if 确认.upper() != "YES":
            print("\n您没有确认已保存助记词。请重新生成并确保安全保存。")
        else:
            print("\n助记词生成完成。请妥善保管您的助记词！")
        
        # 等待用户确认
        input("\n按回车键继续...")
    except Exception as e:
        print(f"\n错误: {str(e)}")
        input("\n按回车键继续...")


def 验证助记词():
    """验证助记词是否有效"""
    # 输入助记词
    print("\n请输入要验证的英文助记词 (词与词之间用空格分隔):")
    助记词 = input()
    
    try:
        生成器 = 钱包生成器()
        是否有效 = 生成器.验证助记词(助记词)
        
        if 是否有效:
            print("\n助记词有效 ✓")
            
            # 询问是否生成种子
            print("\n是否生成种子? (y/n):")
            生成种子选择 = input("> ").lower()
            
            if 生成种子选择 in ['y', 'yes', '是']:
                # 询问密码短语
                print("\n请输入密码短语 (如果没有，直接按回车):")
                密码短语 = input("> ")
                
                # 生成种子
                种子 = 生成器.助记词转种子(助记词, 密码短语)
                种子十六进制 = 种子.hex()
                print(f"\n种子(十六进制): {种子十六进制[:16]}...{种子十六进制[-16:]}")
        else:
            print("\n助记词无效 ✗")
        
        # 等待用户确认
        input("\n按回车键继续...")
    except Exception as e:
        print(f"\n错误: {str(e)}")
        input("\n按回车键继续...")


def 显示安全提示():
    """显示安全提示"""
    print("\n===== 安全提示 =====\n")
    print("1. 助记词是您钱包的主密钥，任何获取它的人都能控制您的资产")
    print("2. 建议在离线环境中生成重要钱包的助记词")
    print("3. 重要提示：本程序不会在本地或云端保存您的助记词")
    print("4. 您必须自己记录并安全保存助记词，否则资产将永久丢失")
    print("5. 永远不要将助记词存储在数字设备上（电脑、手机、云端）")
    print("6. 请务必使用笔和纸或金属助记词板记录下来（防火、防水）")
    print("7. 存放在安全的物理位置，如保险箱")
    print("8. 记录后请使用验证功能确认您的助记词记录正确无误")
    print("9. 使用真随机熵源和足够长度的助记词（推荐24词）")
    
    input("\n按回车键继续...")


def 主程序():
    """主程序入口"""
    while True:
        选择 = 显示菜单()
        
        if 选择 == "1":
            生成新钱包()
        elif 选择 == "2":
            验证助记词()
        elif 选择 == "3":
            print("\n感谢使用！再见！")
            sys.exit(0)
        else:
            print("\n无效选择，请重新输入")


if __name__ == "__main__":
    try:
        主程序()
    except KeyboardInterrupt:
        print("\n\n程序被用户中断。再见！")
        sys.exit(0)
    except Exception as e:
        print(f"\n发生错误: {str(e)}")
        sys.exit(1)