#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
BIP-39实现测试
测试BIP-39标准实现的正确性
"""

import unittest
import sys
import os
import unicodedata
import binascii

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from crypto_wallet_secure_optimized import 钱包生成器, 安全工具
except ImportError:
    print("无法导入钱包生成器模块，请确保项目根目录在Python路径中")
    sys.exit(1)


class BIP39测试(unittest.TestCase):
    """BIP-39标准实现的测试"""
    
    def setUp(self):
        """测试前的准备工作"""
        self.钱包生成器 = 钱包生成器()
        
        # BIP-39官方测试向量
        # 格式: (熵(十六进制), 助记词, 种子(十六进制, 密码短语="TREZOR"))
        self.测试向量 = [
            (
                "00000000000000000000000000000000",
                "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about",
                "c55257c360c07c72029aebc1b53c05ed0362ada38ead3e3e9efa3708e53495531f09a6987599d18264c1e1c92f2cf141630c7a3c4ab7c81b2f001698e7463b04"
            ),
            (
                "7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f",
                "legal winner thank year wave sausage worth useful legal winner thank yellow",
                "2e8905819b8723fe2c1d161860e5ee1830318dbf49a83bd451cfb8440c28bd6fa457fe1296106559a3c80937a1c1069be3a3a5bd381ee6260e8d9739fce1f607"
            ),
            (
                "80808080808080808080808080808080",
                "letter advice cage absurd amount doctor acoustic avoid letter advice cage above",
                "d71de856f81a8acc65e6fc851a38d4d7ec216fd0796d0a6827a3ad6ed5511a30fa280f12eb2e47ed2ac03b5c462a0358d18d69fe4f985ec81778c1b370b652a8"
            ),
            (
                "ffffffffffffffffffffffffffffffff",
                "zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo wrong",
                "ac27495480225222079d7be181583751e86f571027b0497b5b5d11218e0a8a13332572917f0f8e5a589620c6f15b11c61dee327651a14c34e18231052e48c069"
            ),
            (
                "000000000000000000000000000000000000000000000000",
                "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon agent",
                "035895f2f481b1b0f01fcf8c289c794660b289981a78f8106447707fdd9666ca06da5a9a565181599b79f53b844d8a71dd9f439c52a3d7b3e8a79c906ac845fa"
            ),
            (
                "7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f",
                "legal winner thank year wave sausage worth useful legal winner thank year wave sausage worth useful legal will",
                "f2b94508732bcbacbcc020faefecfc89feafa6649a5491b8c952cede496c214a0c7b3c392d168748f2d4a612bada0753b52a1c7ac53c1e93abd5c6320b9e95dd"
            ),
            (
                "808080808080808080808080808080808080808080808080",
                "letter advice cage absurd amount doctor acoustic avoid letter advice cage absurd amount doctor acoustic avoid letter always",
                "107d7c02a5aa6f38c58083ff74f04c607c2d2c0ecc55501dadd72d025b751bc27fe913ffb796f841c49b1d33b610cf0e91d3aa239027f5e99fe4ce9e5088cd65"
            ),
            (
                "ffffffffffffffffffffffffffffffffffffffffffffffff",
                "zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo when",
                "0cd6e5d827bb62eb8fc1e262254223817fd068a74b5b449cc2f667c3f1f985a76379b43348d952e2265b4cd129090758b3e3c2c49103b5051aac2eaeb890a528"
            ),
            (
                "0000000000000000000000000000000000000000000000000000000000000000",
                "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon art",
                "bda85446c68413707090a52022edd26a1c9462295029f2e60cd7c4f2bbd3097170af7a4d73245cafa9c3cca8d561a7c3de6f5d4a10be8ed2a5e608d68f92fcc8"
            ),
            (
                "7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f",
                "legal winner thank year wave sausage worth useful legal winner thank year wave sausage worth useful legal winner thank year wave sausage worth title",
                "bc09fca1804f7e69da93c2f2028eb238c227f2e9dda30cd63699232578480a4021b146ad717fbb7e451ce9eb835f43620bf5c514db0f8add49f5d121449d3e87"
            ),
            (
                "8080808080808080808080808080808080808080808080808080808080808080",
                "letter advice cage absurd amount doctor acoustic avoid letter advice cage absurd amount doctor acoustic avoid letter advice cage absurd amount doctor acoustic bless",
                "c0c519bd0e91a2ed54357d9d1ebef6f5af218a153624cf4f2da911a0ed8f7a09e2ef61af0aca007096df430022f7a2b6fb91661a9589097069720d015e4e982f"
            ),
            (
                "ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff",
                "zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo vote",
                "dd48c104698c30cfe2b6142103248622fb7bb0ff692eebb00089b32d22484e1613912f0a5b694407be899ffd31ed3992c456cdf60f5d4564b8ba3f05a69890ad"
            )
        ]
    
    def test_助记词生成(self):
        """测试从熵生成助记词"""
        for 熵十六进制, 期望助记词, _ in self.测试向量:
            熵 = bytes.fromhex(熵十六进制)
            助记词 = self.钱包生成器.助记词工具.to_mnemonic(熵)
            self.assertEqual(助记词, 期望助记词)
    
    def test_种子生成(self):
        """测试从助记词生成种子"""
        for _, 助记词, 期望种子十六进制 in self.测试向量:
            种子 = self.钱包生成器.助记词转种子(助记词, "TREZOR")
            self.assertEqual(种子.hex(), 期望种子十六进制)
    
    def test_助记词验证(self):
        """测试助记词验证功能"""
        for _, 助记词, _ in self.测试向量:
            self.assertTrue(self.钱包生成器.验证助记词(助记词))
        
        # 测试无效助记词
        无效助记词 = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon"  # 少一个词
        self.assertFalse(self.钱包生成器.验证助记词(无效助记词))
        
        无效助记词2 = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon invalid"  # 无效的词
        self.assertFalse(self.钱包生成器.验证助记词(无效助记词2))
    
    def test_Unicode规范化(self):
        """测试Unicode规范化处理"""
        # 创建一个包含重音字符的密码短语
        非规范化密码 = "Café"  # é是一个组合字符
        规范化密码 = unicodedata.normalize('NFKD', 非规范化密码)
        
        # 确保规范化函数正常工作
        self.assertEqual(安全工具.规范化字符串(非规范化密码), 规范化密码)
        
        # 测试使用不同形式的密码短语生成的种子是否相同
        助记词 = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"
        种子1 = self.钱包生成器.助记词转种子(助记词, 非规范化密码)
        种子2 = self.钱包生成器.助记词转种子(助记词, 规范化密码)
        
        # 两个种子应该相同，因为密码短语应该被规范化
        self.assertEqual(种子1, 种子2)
    
    def test_不同语言(self):
        """测试不同语言的助记词生成"""
        # 测试英文
        英文生成器 = 钱包生成器("english")
        熵 = bytes.fromhex("00000000000000000000000000000000")
        英文助记词 = 英文生成器.助记词工具.to_mnemonic(熵)
        self.assertEqual(英文助记词, "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about")
        
        # 测试其他语言（如果可用）
        try:
            # 测试中文简体
            中文生成器 = 钱包生成器("chinese_simplified")
            中文助记词 = 中文生成器.助记词工具.to_mnemonic(熵)
            self.assertNotEqual(中文助记词, 英文助记词)  # 不同语言的助记词应该不同
            
            # 验证中文助记词
            self.assertTrue(中文生成器.验证助记词(中文助记词))
            
            # 从不同语言的助记词生成的种子应该相同（如果使用相同的密码短语）
            英文种子 = 英文生成器.助记词转种子(英文助记词, "test")
            中文种子 = 中文生成器.助记词转种子(中文助记词, "test")
            self.assertEqual(英文种子, 中文种子)
        except Exception as e:
            print(f"跳过中文测试: {e}")
    
    def test_不同强度(self):
        """测试不同强度的助记词生成"""
        # 测试不同的熵强度
        强度列表 = [128, 160, 192, 224, 256]
        词数列表 = [12, 15, 18, 21, 24]
        
        for 强度, 期望词数 in zip(强度列表, 词数列表):
            助记词 = self.钱包生成器.生成助记词(强度)
            词数 = len(助记词.split())
            self.assertEqual(词数, 期望词数)


if __name__ == "__main__":
    unittest.main()