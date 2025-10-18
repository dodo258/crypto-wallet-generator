#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
加密货币钱包助记词生成工具
使用真随机熵源生成符合BIP39标准的助记词
"""

import os
import sys
import click
import hashlib
from typing import List, Optional
from mnemonic import Mnemonic
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes

class EntropyGenerator:
    """真随机熵源生成器"""
    
    @staticmethod
    def get_system_entropy(num_bytes: int) -> bytes:
        """
        从操作系统获取真随机熵
        
        Args:
            num_bytes: 需要的字节数
            
        Returns:
            随机字节
        """
        try:
            return os.urandom(num_bytes)
        except NotImplementedError:
            raise RuntimeError("当前系统不支持os.urandom，无法获取系统随机熵")
    
    @staticmethod
    def get_mixed_entropy(num_bytes: int) -> bytes:
        """
        混合多种熵源获取更高质量的随机性
        
        Args:
            num_bytes: 需要的字节数
            
        Returns:
            随机字节
        """
        # 系统熵
        system_entropy = EntropyGenerator.get_system_entropy(num_bytes)
        
        # 创建一个哈希对象来混合熵源
        hasher = hashlib.sha512()
        
        # 添加系统熵
        hasher.update(system_entropy)
        
        # 添加当前时间微秒级精度
        import time
        hasher.update(str(time.time()).encode())
        
        # 如果可能，添加硬件随机性
        try:
            # 尝试读取/dev/random (仅在类Unix系统上可用)
            if os.path.exists('/dev/random'):
                with open('/dev/random', 'rb') as f:
                    hasher.update(f.read(32))
        except:
            pass
        
        # 生成一些计算随机性
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        hasher.update(str(id(private_key)).encode())
        
        # 获取最终哈希
        final_hash = hasher.digest()
        
        # 确保返回正确的字节数
        return final_hash[:num_bytes]


class WalletGenerator:
    """钱包助记词生成器"""
    
    def __init__(self, language: str = "english"):
        """
        初始化钱包生成器
        
        Args:
            language: 助记词语言，支持 english, chinese_simplified, chinese_traditional, 
                     french, italian, japanese, korean, spanish
        """
        self.language = language
        self.mnemonic = Mnemonic(language)
    
    def generate_mnemonic(self, strength: int = 128) -> str:
        """
        生成助记词
        
        Args:
            strength: 熵的位数，必须是32的倍数，范围是128-256
                     128位生成12个词，256位生成24个词
        
        Returns:
            助记词字符串
        """
        if strength % 32 != 0 or strength < 128 or strength > 256:
            raise ValueError("熵的位数必须是32的倍数，范围是128-256")
        
        # 计算需要的字节数
        num_bytes = strength // 8
        
        # 获取真随机熵
        entropy = EntropyGenerator.get_mixed_entropy(num_bytes)
        
        # 生成助记词
        return self.mnemonic.to_mnemonic(entropy)
    
    def verify_mnemonic(self, mnemonic: str) -> bool:
        """
        验证助记词是否有效
        
        Args:
            mnemonic: 助记词字符串
            
        Returns:
            是否有效
        """
        return self.mnemonic.check(mnemonic)
    
    def mnemonic_to_seed(self, mnemonic: str, passphrase: str = "") -> bytes:
        """
        将助记词转换为种子
        
        Args:
            mnemonic: 助记词字符串
            passphrase: 可选密码短语
            
        Returns:
            种子字节
        """
        return self.mnemonic.to_seed(mnemonic, passphrase)


@click.group()
def cli():
    """加密货币钱包助记词生成工具"""
    pass


@cli.command()
@click.option('--strength', '-s', default=128, 
              help='熵的位数 (128, 160, 192, 224, 256)。128位生成12个词，256位生成24个词')
@click.option('--language', '-l', default='english',
              type=click.Choice(['english', 'chinese_simplified', 'chinese_traditional', 
                               'french', 'italian', 'japanese', 'korean', 'spanish']),
              help='助记词语言')
@click.option('--words', '-w', default=None, type=int,
              help='助记词数量 (12, 15, 18, 21, 24)，会覆盖strength参数')
def generate(strength: int, language: str, words: Optional[int]):
    """生成新的钱包助记词"""
    # 如果指定了words参数，转换为对应的strength
    if words is not None:
        word_to_strength = {
            12: 128,
            15: 160,
            18: 192,
            21: 224,
            24: 256
        }
        if words not in word_to_strength:
            click.echo(f"错误: 助记词数量必须是 {', '.join(map(str, word_to_strength.keys()))} 之一")
            sys.exit(1)
        strength = word_to_strength[words]
    
    try:
        generator = WalletGenerator(language)
        mnemonic = generator.generate_mnemonic(strength)
        click.echo("\n生成的助记词:")
        click.echo(f"\n{mnemonic}\n")
        click.echo(f"语言: {language}")
        click.echo(f"词数: {len(mnemonic.split())}")
        click.echo("\n警告: 请将助记词安全保存，任何人获取到助记词将可以控制您的加密资产！")
    except Exception as e:
        click.echo(f"错误: {str(e)}")
        sys.exit(1)


@cli.command()
@click.argument('mnemonic')
@click.option('--language', '-l', default='english',
              type=click.Choice(['english', 'chinese_simplified', 'chinese_traditional', 
                               'french', 'italian', 'japanese', 'korean', 'spanish']),
              help='助记词语言')
def verify(mnemonic: str, language: str):
    """验证助记词是否有效"""
    try:
        generator = WalletGenerator(language)
        is_valid = generator.verify_mnemonic(mnemonic)
        if is_valid:
            click.echo("助记词有效 ✓")
        else:
            click.echo("助记词无效 ✗")
            sys.exit(1)
    except Exception as e:
        click.echo(f"错误: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    cli()