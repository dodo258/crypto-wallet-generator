#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
高安全标准加密货币钱包助记词生成工具
遵循BIP-39标准，使用多源熵生成符合密码学安全要求的英文助记词
支持SLIP-39分割备份方案

安全特性:
- 使用操作系统CSPRNG和多源熵混合
- 支持离线生成和验证
- 提供完整的安全提示和用户教育
- 支持SLIP-39分割备份
- 实现内存安全处理
"""

import os
import sys
import hashlib
import time
import secrets
import unicodedata
import getpass
import ctypes
import platform
import random
import json
from typing import List, Dict, Tuple, Optional, Union, Any
from pathlib import Path

try:
    from mnemonic import Mnemonic
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.backends import default_backend
    
    # 尝试导入SLIP-39库，如果安装了的话
    try:
        import shamir_mnemonic
        SLIP39_AVAILABLE = True
    except ImportError:
        SLIP39_AVAILABLE = False
except ImportError:
    print("错误: 缺少必要的依赖库。请运行: pip install cryptography mnemonic")
    print("如需SLIP-39支持，请运行: pip install shamir-mnemonic")
    sys.exit(1)


# 安全常量
DEFAULT_ENTROPY_BITS = 256  # 默认使用256位熵（24个词）
MIN_ENTROPY_BITS = 128      # 最小允许128位熵（12个词）
PBKDF2_ITERATIONS = 2048    # BIP-39标准迭代次数
ENTROPY_SOURCES_REQUIRED = 3  # 要求至少3个熵源
DEFAULT_LANGUAGE = "english"  # 默认使用英文助记词


class 安全工具:
    """安全相关的工具函数"""
    
    @staticmethod
    def 安全清除内存(数据):
        """
        安全清除内存中的敏感数据
        
        参数:
            数据: 要清除的数据对象
        """
        if isinstance(数据, bytes):
            # 对于字节类型，用随机数据覆盖
            长度 = len(数据)
            ctypes.memset(ctypes.cast(数据, ctypes.POINTER(ctypes.c_char)), 0, 长度)
        elif isinstance(数据, str):
            # 对于字符串，无法直接覆盖，但可以尝试删除引用
            数据 = None
        elif isinstance(数据, list):
            # 对于列表，清除每个元素
            for i in range(len(数据)):
                安全工具.安全清除内存(数据[i])
                数据[i] = None
        elif isinstance(数据, dict):
            # 对于字典，清除每个值
            for key in 数据:
                安全工具.安全清除内存(数据[key])
                数据[key] = None
    
    @staticmethod
    def 规范化字符串(文本: str) -> str:
        """
        对字符串进行NFKD Unicode规范化处理
        
        参数:
            文本: 要规范化的字符串
            
        返回:
            规范化后的字符串
        """
        return unicodedata.normalize('NFKD', 文本)
    
    @staticmethod
    def 检查系统安全性() -> Dict[str, bool]:
        """
        检查系统安全状态
        
        返回:
            包含安全检查结果的字典
        """
        结果 = {}
        
        # 检查是否为离线环境（简单检查，不完全可靠）
        try:
            import socket
            socket.create_connection(("www.baidu.com", 80), timeout=1)
            结果["离线环境"] = False
        except:
            结果["离线环境"] = True
        
        # 检查操作系统类型
        结果["操作系统"] = platform.system()
        
        # 检查是否有安全的随机源
        try:
            os.urandom(16)
            结果["安全随机源"] = True
        except NotImplementedError:
            结果["安全随机源"] = False
        
        # 检查是否有硬件随机源
        结果["硬件随机源"] = os.path.exists('/dev/hwrng')
        
        return 结果


class 熵池:
    """熵池管理器，负责收集和混合多源熵"""
    
    def __init__(self):
        """初始化熵池"""
        self.熵源计数 = 0
        self.熵池 = hashlib.sha512()
        self.已添加熵源 = set()
    
    def 添加熵(self, 熵源名称: str, 熵数据: bytes) -> None:
        """
        向熵池添加熵
        
        参数:
            熵源名称: 熵源的名称标识
            熵数据: 熵数据
        """
        if 熵源名称 not in self.已添加熵源:
            self.熵池.update(熵数据)
            self.熵源计数 += 1
            self.已添加熵源.add(熵源名称)
    
    def 获取熵池状态(self) -> Dict[str, Any]:
        """
        获取熵池当前状态
        
        返回:
            包含熵池状态的字典
        """
        return {
            "熵源数量": self.熵源计数,
            "已添加熵源": list(self.已添加熵源),
            "熵池健康度": min(100, self.熵源计数 * 100 // ENTROPY_SOURCES_REQUIRED)
        }
    
    def 熵池是否健康(self) -> bool:
        """
        检查熵池是否有足够的熵源
        
        返回:
            如果熵池有足够的熵源，返回True
        """
        return self.熵源计数 >= ENTROPY_SOURCES_REQUIRED
    
    def 获取熵(self, 字节数: int) -> bytes:
        """
        从熵池获取指定字节数的熵
        
        参数:
            字节数: 需要的字节数
            
        返回:
            随机字节
        
        异常:
            ValueError: 如果熵池不健康
        """
        if not self.熵池是否健康():
            raise ValueError(f"熵池不健康，当前熵源数量: {self.熵源计数}，需要至少: {ENTROPY_SOURCES_REQUIRED}")
        
        # 获取当前熵池的哈希
        当前哈希 = self.熵池.digest()
        
        # 创建一个新的哈希对象用于扩展熵
        扩展哈希 = hashlib.sha512()
        扩展哈希.update(当前哈希)
        
        # 如果需要的字节数超过了哈希长度，则需要扩展
        结果 = bytearray()
        剩余字节 = 字节数
        计数器 = 0
        
        while 剩余字节 > 0:
            # 添加计数器以生成不同的哈希
            计数器哈希 = hashlib.sha512()
            计数器哈希.update(当前哈希)
            计数器哈希.update(计数器.to_bytes(4, byteorder='big'))
            
            哈希结果 = 计数器哈希.digest()
            取用字节数 = min(len(哈希结果), 剩余字节)
            结果.extend(哈希结果[:取用字节数])
            
            剩余字节 -= 取用字节数
            计数器 += 1
        
        return bytes(结果)


class 熵源生成器:
    """负责从多种来源收集熵"""
    
    def __init__(self):
        """初始化熵源生成器"""
        self.熵池 = 熵池()
    
    def 收集系统熵(self) -> None:
        """从操作系统的CSPRNG收集熵"""
        try:
            系统熵 = os.urandom(64)
            self.熵池.添加熵("系统CSPRNG", 系统熵)
        except NotImplementedError:
            print("警告: 当前系统不支持os.urandom，无法获取系统随机熵")
    
    def 收集Python安全熵(self) -> None:
        """从Python的secrets模块收集熵"""
        try:
            安全熵 = secrets.token_bytes(64)
            self.熵池.添加熵("Python_secrets", 安全熵)
        except Exception:
            print("警告: 无法从Python的secrets模块获取熵")
    
    def 收集时间熵(self) -> None:
        """从高精度时间收集熵（弱熵源，仅作为补充）"""
        时间哈希 = hashlib.sha256()
        
        # 收集多个时间点以增加熵
        for _ in range(10):
            时间哈希.update(str(time.time_ns()).encode())
            time.sleep(0.01)  # 微小延迟以获取不同时间
        
        self.熵池.添加熵("时间熵", 时间哈希.digest())
    
    def 收集硬件熵(self) -> None:
        """尝试从硬件随机源收集熵"""
        try:
            # 尝试读取/dev/hwrng (硬件随机数生成器)
            if os.path.exists('/dev/hwrng'):
                with open('/dev/hwrng', 'rb') as f:
                    硬件熵 = f.read(64)
                    self.熵池.添加熵("硬件RNG", 硬件熵)
            # 尝试读取/dev/random (高质量熵池)
            elif os.path.exists('/dev/random'):
                with open('/dev/random', 'rb') as f:
                    随机设备熵 = f.read(64)
                    self.熵池.添加熵("dev_random", 随机设备熵)
        except:
            pass
    
    def 收集计算熵(self) -> None:
        """通过计算密集型操作生成熵"""
        try:
            # 生成RSA密钥对是计算密集型的，可以作为熵源
            私钥 = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048
            )
            # 使用私钥的内存地址和对象ID作为熵
            计算熵 = hashlib.sha256()
            计算熵.update(str(id(私钥)).encode())
            计算熵.update(str(私钥.private_numbers().d).encode())
            
            self.熵池.添加熵("计算熵", 计算熵.digest())
        except:
            pass
    
    def 收集用户熵(self, 用户输入: str = None) -> None:
        """
        从用户输入收集熵
        
        参数:
            用户输入: 用户提供的熵字符串，如果为None则提示用户输入
        """
        if 用户输入 is None:
            print("\n为增强随机性，请输入一些随机字符（按回车结束）:")
            用户输入 = getpass.getpass("（输入内容不会显示）: ")
        
        if 用户输入:
            用户熵 = hashlib.sha256(用户输入.encode()).digest()
            self.熵池.添加熵("用户输入", 用户熵)
    
    def 收集所有可用熵(self, 包含用户熵: bool = True) -> None:
        """
        收集所有可用的熵源
        
        参数:
            包含用户熵: 是否包含用户输入的熵
        """
        self.收集系统熵()
        self.收集Python安全熵()
        self.收集时间熵()
        self.收集硬件熵()
        self.收集计算熵()
        
        if 包含用户熵:
            self.收集用户熵()
    
    def 获取熵(self, 字节数: int) -> bytes:
        """
        获取指定字节数的熵
        
        参数:
            字节数: 需要的字节数
            
        返回:
            随机字节
        """
        # 确保熵池健康
        if not self.熵池.熵池是否健康():
            print("警告: 熵池不够健康，正在收集更多熵...")
            self.收集所有可用熵(包含用户熵=True)
        
        return self.熵池.获取熵(字节数)
    
    def 获取熵池状态(self) -> Dict[str, Any]:
        """
        获取熵池状态
        
        返回:
            熵池状态字典
        """
        return self.熵池.获取熵池状态()


class 钱包生成器:
    """钱包助记词生成器，遵循BIP-39标准"""
    
    def __init__(self):
        """
        初始化钱包生成器，只使用英文助记词
        """
        self.语言 = DEFAULT_LANGUAGE
        self.助记词工具 = Mnemonic(self.语言)
        self.熵源生成器 = 熵源生成器()
    
    def 生成助记词(self, 强度: int = DEFAULT_ENTROPY_BITS) -> str:
        """
        生成BIP-39标准助记词
        
        参数:
            强度: 熵的位数，必须是32的倍数，范围是128-256
                 128位生成12个词，256位生成24个词
        
        返回:
            助记词字符串
        """
        if 强度 % 32 != 0 or 强度 < MIN_ENTROPY_BITS or 强度 > 256:
            raise ValueError(f"熵的位数必须是32的倍数，范围是{MIN_ENTROPY_BITS}-256")
        
        # 收集所有可用熵
        self.熵源生成器.收集所有可用熵()
        
        # 计算需要的字节数
        字节数 = 强度 // 8
        
        # 获取熵
        熵 = self.熵源生成器.获取熵(字节数)
        
        # 生成助记词
        助记词 = self.助记词工具.to_mnemonic(熵)
        
        return 助记词
    
    def 验证助记词(self, 助记词: str) -> bool:
        """
        验证助记词是否有效
        
        参数:
            助记词: 助记词字符串
            
        返回:
            是否有效
        """
        # 对助记词进行NFKD规范化
        规范化助记词 = 安全工具.规范化字符串(助记词)
        return self.助记词工具.check(规范化助记词)
    
    def 助记词转种子(self, 助记词: str, 密码: str = "") -> bytes:
        """
        将助记词转换为种子
        
        参数:
            助记词: 助记词字符串
            密码: 可选密码短语
            
        返回:
            种子字节
        """
        # 对助记词和密码进行NFKD规范化
        规范化助记词 = 安全工具.规范化字符串(助记词)
        规范化密码 = 安全工具.规范化字符串(密码)
        
        # 使用BIP-39标准的PBKDF2函数
        种子 = self.助记词工具.to_seed(规范化助记词, 规范化密码)
        
        return 种子


class SLIP39管理器:
    """SLIP-39 Shamir备份管理器"""
    
    def __init__(self):
        """初始化SLIP-39管理器"""
        if not SLIP39_AVAILABLE:
            raise ImportError("SLIP-39功能需要安装shamir-mnemonic库")
    
    def 生成分享(self, 主秘密: bytes, 组数: int, 阈值: int, 
              每组成员数: List[int], 每组阈值: List[int], 
              密码: str = "") -> List[List[str]]:
        """
        将主秘密分割为多个分享
        
        参数:
            主秘密: 要分割的主秘密
            组数: 分组数量
            阈值: 恢复所需的组数量
            每组成员数: 每个组的成员数量列表
            每组阈值: 每个组的阈值列表
            密码: 可选密码短语
            
        返回:
            分享列表的列表，每个内部列表代表一个组的所有分享
        """
        # 对密码进行NFKD规范化
        规范化密码 = 安全工具.规范化字符串(密码)
        
        # 生成分享
        所有分享 = shamir_mnemonic.generate_mnemonics(
            group_threshold=阈值,
            groups=[(每组阈值[i], 每组成员数[i]) for i in range(组数)],
            master_secret=主秘密,
            passphrase=规范化密码.encode()
        )
        
        return 所有分享
    
    def 恢复秘密(self, 分享列表: List[str], 密码: str = "") -> bytes:
        """
        从分享中恢复主秘密
        
        参数:
            分享列表: SLIP-39分享列表
            密码: 可选密码短语
            
        返回:
            恢复的主秘密
        """
        # 对密码进行NFKD规范化
        规范化密码 = 安全工具.规范化字符串(密码)
        
        # 恢复主秘密
        主秘密 = shamir_mnemonic.combine_mnemonics(分享列表, 规范化密码.encode())
        
        return 主秘密


def 显示安全提示(提示类型: str) -> None:
    """
    显示安全提示
    
    参数:
        提示类型: 提示类型
    """
    提示 = {
        "生成前": [
            "⚠️ 安全警告：助记词是您钱包的主密钥，任何获取它的人都能控制您的资产",
            "✓ 确保您处于安全的环境，无摄像头、无屏幕录制、无恶意软件",
            "✓ 建议在离线环境中生成重要钱包的助记词",
            "✓ 使用真随机熵源和足够长度的助记词（推荐24词）"
        ],
        "生成后": [
            "⚠️ 永远不要将助记词存储在数字设备上（电脑、手机、云端）",
            "✓ 将助记词写在纸上或金属板上（防火、防水）",
            "✓ 存放在安全的物理位置，如保险箱",
            "✓ 考虑使用SLIP-39分割备份，分散存储在不同安全位置",
            "✓ 定期验证您的备份是否可用"
        ],
        "密码短语": [
            "⚠️ 密码短语(passphrase)是BIP-39的可选第25个词",
            "✓ 增加了安全性，但也增加了丢失风险",
            "✓ 如果忘记密码短语，即使有助记词也无法恢复资产",
            "✓ 密码短语应当单独保存，与助记词分开存放"
        ],
        "SLIP39": [
            "⚠️ SLIP-39允许将助记词分割成多个部分，需要达到阈值数量才能恢复",
            "✓ 可以设置多个组，每组有多个成员和阈值",
            "✓ 增强了安全性和可靠性，防止单点故障",
            "✓ 每个分享应当分开存放在不同的安全位置"
        ]
    }
    
    if 提示类型 in 提示:
        print(f"\n===== {提示类型}安全提示 =====")
        for 行 in 提示[提示类型]:
            print(行)
        print()


def 显示菜单() -> str:
    """
    显示主菜单
    
    返回:
        用户选择
    """
    print("\n===== 高安全标准加密货币钱包助记词生成工具 =====\n")
    print("1. 生成新的钱包助记词")
    print("2. 验证助记词是否有效")
    print("3. 生成SLIP-39分割备份")
    print("4. 恢复SLIP-39分割备份")
    print("5. 检查系统安全状态")
    print("6. 退出程序")
    
    选择 = input("\n请输入选项 (1-6): ")
    return 选择


def 选择助记词长度() -> int:
    """
    选择助记词长度
    
    返回:
        熵的位数
    """
    print("\n===== 选择助记词长度 =====\n")
    print("1. 24个词 (256位熵，最高安全性，推荐)")
    print("2. 21个词 (224位熵)")
    print("3. 18个词 (192位熵)")
    print("4. 15个词 (160位熵)")
    print("5. 12个词 (128位熵，安全性较低，不推荐用于高价值钱包)")
    
    长度映射 = {
        "1": 256,
        "2": 224,
        "3": 192,
        "4": 160,
        "5": 128
    }
    
    while True:
        选择 = input("\n请输入选项 (1-5): ")
        if 选择 in 长度映射:
            return 长度映射[选择]
        else:
            print("无效选择，请重新输入")


def 是否使用密码短语() -> Tuple[bool, str]:
    """
    询问是否使用密码短语
    
    返回:
        (是否使用密码短语, 密码短语)
    """
    显示安全提示("密码短语")
    
    while True:
        选择 = input("\n是否使用密码短语(passphrase)? (y/n): ").lower()
        if 选择 in ['y', 'yes', '是']:
            print("\n请输入密码短语 (将不会显示在屏幕上):")
            密码短语 = getpass.getpass()
            print("请再次输入密码短语确认:")
            确认密码 = getpass.getpass()
            
            if 密码短语 == 确认密码:
                return True, 密码短语
            else:
                print("两次输入的密码短语不匹配，请重新输入")
        elif 选择 in ['n', 'no', '否']:
            return False, ""
        else:
            print("无效选择，请输入 y 或 n")


def 生成新钱包() -> None:
    """生成新的钱包助记词"""
    显示安全提示("生成前")
    
    # 选择助记词长度
    强度 = 选择助记词长度()
    
    # 询问是否使用密码短语
    使用密码短语, 密码短语 = 是否使用密码短语()
    
    print("\n正在收集熵源，这可能需要一些时间...")
    
    try:
        # 创建钱包生成器
        生成器 = 钱包生成器()
        
        # 显示熵池状态
        熵池状态 = 生成器.熵源生成器.获取熵池状态()
        print(f"\n熵池状态: {熵池状态['熵池健康度']}% ({熵池状态['熵源数量']}/{ENTROPY_SOURCES_REQUIRED}个熵源)")
        print(f"已添加熵源: {', '.join(熵池状态['已添加熵源'])}")
        
        # 生成助记词
        助记词 = 生成器.生成助记词(强度)
        
        # 如果使用密码短语，生成种子
        if 使用密码短语:
            种子 = 生成器.助记词转种子(助记词, 密码短语)
            种子十六进制 = 种子.hex()
        
        print("\n===== 生成的助记词 =====\n")
        print(f"{助记词}\n")
        print(f"语言: {DEFAULT_LANGUAGE} (英文)")
        print(f"词数: {len(助记词.split())}")
        
        if 使用密码短语:
            print(f"使用了密码短语: 是")
            print(f"种子(十六进制): {种子十六进制[:16]}...{种子十六进制[-16:]}")
        
        显示安全提示("生成后")
        
        # 验证用户已抄写助记词
        print("\n请确认您已安全抄写并保存了助记词")
        确认 = input("输入 'YES' 确认: ")
        
        if 确认.upper() != "YES":
            print("\n您没有确认已保存助记词。请重新生成并确保安全保存。")
        else:
            print("\n助记词生成完成。请妥善保管您的助记词！")
        
        # 清除敏感数据
        安全工具.安全清除内存(助记词)
        if 使用密码短语:
            安全工具.安全清除内存(密码短语)
            安全工具.安全清除内存(种子)
            安全工具.安全清除内存(种子十六进制)
        
        # 等待用户确认
        input("\n按回车键继续...")
    except Exception as e:
        print(f"\n错误: {str(e)}")
        input("\n按回车键继续...")


def 验证助记词() -> None:
    """验证助记词是否有效"""
    # 输入助记词
    print("\n请输入要验证的英文助记词 (词与词之间用空格分隔):")
    助记词 = input()
    
    # 询问是否使用密码短语
    使用密码短语, 密码短语 = 是否使用密码短语()
    
    try:
        生成器 = 钱包生成器()
        是否有效 = 生成器.验证助记词(助记词)
        
        if 是否有效:
            print("\n助记词有效 ✓")
            
            if 使用密码短语:
                # 生成种子
                种子 = 生成器.助记词转种子(助记词, 密码短语)
                种子十六进制 = 种子.hex()
                print(f"\n种子(十六进制): {种子十六进制[:16]}...{种子十六进制[-16:]}")
                
                # 清除敏感数据
                安全工具.安全清除内存(种子)
                安全工具.安全清除内存(种子十六进制)
        else:
            print("\n助记词无效 ✗")
        
        # 清除敏感数据
        安全工具.安全清除内存(助记词)
        if 使用密码短语:
            安全工具.安全清除内存(密码短语)
        
        # 等待用户确认
        input("\n按回车键继续...")
    except Exception as e:
        print(f"\n错误: {str(e)}")
        input("\n按回车键继续...")


def 生成SLIP39分割() -> None:
    """生成SLIP-39分割备份"""
    if not SLIP39_AVAILABLE:
        print("\n错误: SLIP-39功能需要安装shamir-mnemonic库")
        print("请运行: pip install shamir-mnemonic")
        input("\n按回车键继续...")
        return
    
    显示安全提示("SLIP39")
    
    # 询问是否使用密码短语
    使用密码短语, 密码短语 = 是否使用密码短语()
    
    # 输入助记词或生成新的
    print("\n请选择:")
    print("1. 输入现有BIP-39助记词进行分割")
    print("2. 生成新的助记词并分割")
    
    选择 = input("\n请输入选项 (1-2): ")
    
    try:
        生成器 = 钱包生成器()
        slip39管理器 = SLIP39管理器()
        
        if 选择 == "1":
            print("\n请输入BIP-39英文助记词 (词与词之间用空格分隔):")
            助记词 = input()
            
            # 验证助记词
            if not 生成器.验证助记词(助记词):
                print("\n错误: 无效的BIP-39助记词")
                input("\n按回车键继续...")
                return
            
            # 转换为种子
            主秘密 = 生成器.助记词转种子(助记词, 密码短语 if 使用密码短语 else "")
        else:
            # 选择助记词长度
            强度 = 选择助记词长度()
            
            # 生成新助记词
            助记词 = 生成器.生成助记词(强度)
            print("\n生成的BIP-39助记词:")
            print(f"{助记词}\n")
            
            # 转换为种子
            主秘密 = 生成器.助记词转种子(助记词, 密码短语 if 使用密码短语 else "")
        
        # 配置SLIP-39分割
        print("\n===== SLIP-39分割配置 =====")
        
        # 组数
        while True:
            try:
                组数 = int(input("\n请输入组数 (1-16): "))
                if 1 <= 组数 <= 16:
                    break
                print("组数必须在1到16之间")
            except ValueError:
                print("请输入有效的数字")
        
        # 恢复所需组数
        while True:
            try:
                恢复组数 = int(input(f"\n请输入恢复所需的组数 (1-{组数}): "))
                if 1 <= 恢复组数 <= 组数:
                    break
                print(f"恢复组数必须在1到{组数}之间")
            except ValueError:
                print("请输入有效的数字")
        
        每组成员数 = []
        每组阈值 = []
        
        # 配置每个组
        for i in range(组数):
            print(f"\n===== 组 {i+1} 配置 =====")
            
            # 成员数
            while True:
                try:
                    成员数 = int(input(f"请输入组 {i+1} 的成员数 (1-16): "))
                    if 1 <= 成员数 <= 16:
                        每组成员数.append(成员数)
                        break
                    print("成员数必须在1到16之间")
                except ValueError:
                    print("请输入有效的数字")
            
            # 阈值
            while True:
                try:
                    阈值 = int(input(f"请输入组 {i+1} 恢复所需的成员数 (1-{成员数}): "))
                    if 1 <= 阈值 <= 成员数:
                        每组阈值.append(阈值)
                        break
                    print(f"阈值必须在1到{成员数}之间")
                except ValueError:
                    print("请输入有效的数字")
        
        # 询问SLIP-39密码短语
        print("\n是否为SLIP-39分享设置额外的密码短语? (与BIP-39密码短语不同)")
        slip39密码 = ""
        if input("(y/n): ").lower() in ['y', 'yes', '是']:
            print("\n请输入SLIP-39密码短语 (将不会显示在屏幕上):")
            slip39密码 = getpass.getpass()
            print("请再次输入SLIP-39密码短语确认:")
            确认密码 = getpass.getpass()
            
            if slip39密码 != 确认密码:
                print("\n两次输入的密码短语不匹配，将不使用密码短语")
                slip39密码 = ""
        
        # 生成SLIP-39分享
        分享列表 = slip39管理器.生成分享(
            主秘密=主秘密,
            组数=组数,
            阈值=恢复组数,
            每组成员数=每组成员数,
            每组阈值=每组阈值,
            密码=slip39密码
        )
        
        # 显示分享
        print("\n===== SLIP-39分享 =====\n")
        print("请安全记录以下分享，并分别保存在不同的安全位置:\n")
        
        for i, 组 in enumerate(分享列表):
            print(f"组 {i+1}:")
            for j, 分享 in enumerate(组):
                print(f"  成员 {j+1}: {分享}")
            print()
        
        print("\n恢复说明:")
        print(f"- 需要至少 {恢复组数} 个组的有效分享才能恢复")
        for i in range(组数):
            print(f"- 组 {i+1} 需要至少 {每组阈值[i]} 个成员的分享")
        
        # 清除敏感数据
        安全工具.安全清除内存(助记词)
        安全工具.安全清除内存(主秘密)
        if 使用密码短语:
            安全工具.安全清除内存(密码短语)
        if slip39密码:
            安全工具.安全清除内存(slip39密码)
        
        # 等待用户确认
        input("\n按回车键继续...")
    except Exception as e:
        print(f"\n错误: {str(e)}")
        input("\n按回车键继续...")


def 恢复SLIP39分割() -> None:
    """恢复SLIP-39分割备份"""
    if not SLIP39_AVAILABLE:
        print("\n错误: SLIP-39功能需要安装shamir-mnemonic库")
        print("请运行: pip install shamir-mnemonic")
        input("\n按回车键继续...")
        return
    
    try:
        slip39管理器 = SLIP39管理器()
        
        # 询问SLIP-39密码短语
        slip39密码 = ""
        if input("\n是否使用SLIP-39密码短语? (y/n): ").lower() in ['y', 'yes', '是']:
            print("\n请输入SLIP-39密码短语 (将不会显示在屏幕上):")
            slip39密码 = getpass.getpass()
        
        # 收集分享
        分享列表 = []
        print("\n请输入SLIP-39分享 (每行一个，输入空行结束):")
        
        while True:
            分享 = input()
            if not 分享:
                break
            分享列表.append(分享)
        
        if len(分享列表) < 1:
            print("\n错误: 至少需要输入一个分享")
            input("\n按回车键继续...")
            return
        
        # 恢复主秘密
        主秘密 = slip39管理器.恢复秘密(分享列表, slip39密码)
        
        # 显示恢复的种子
        print("\n成功恢复主秘密!")
        种子十六进制 = 主秘密.hex()
        print(f"种子(十六进制): {种子十六进制[:16]}...{种子十六进制[-16:]}")
        
        # 清除敏感数据
        安全工具.安全清除内存(主秘密)
        安全工具.安全清除内存(种子十六进制)
        if slip39密码:
            安全工具.安全清除内存(slip39密码)
        
        # 等待用户确认
        input("\n按回车键继续...")
    except Exception as e:
        print(f"\n错误: {str(e)}")
        input("\n按回车键继续...")


def 检查系统安全状态() -> None:
    """检查系统安全状态"""
    print("\n正在检查系统安全状态...")
    
    安全状态 = 安全工具.检查系统安全性()
    
    print("\n===== 系统安全状态 =====\n")
    print(f"操作系统: {安全状态['操作系统']}")
    print(f"离线环境: {'是' if 安全状态['离线环境'] else '否'}")
    print(f"安全随机源: {'可用' if 安全状态['安全随机源'] else '不可用'}")
    print(f"硬件随机源: {'可用' if 安全状态['硬件随机源'] else '不可用'}")
    
    # 安全建议
    print("\n安全建议:")
    if not 安全状态['离线环境']:
        print("⚠️ 警告: 您似乎处于联网环境。建议在离线环境中生成重要钱包的助记词。")
    
    if not 安全状态['安全随机源']:
        print("⚠️ 严重警告: 您的系统似乎没有安全的随机源。不建议在此环境生成钱包!")
    
    if not 安全状态['硬件随机源']:
        print("ℹ️ 提示: 您的系统没有检测到硬件随机源。这是正常的，但如有条件，建议使用带有硬件随机数生成器的设备。")
    
    # 等待用户确认
    input("\n按回车键继续...")


def 主程序() -> None:
    """主程序入口"""
    while True:
        选择 = 显示菜单()
        
        if 选择 == "1":
            生成新钱包()
        elif 选择 == "2":
            验证助记词()
        elif 选择 == "3":
            生成SLIP39分割()
        elif 选择 == "4":
            恢复SLIP39分割()
        elif 选择 == "5":
            检查系统安全状态()
        elif 选择 == "6":
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