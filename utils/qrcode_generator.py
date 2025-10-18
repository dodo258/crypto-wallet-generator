#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
二维码生成工具
用于将助记词或其他敏感信息转换为二维码
"""

import os
import io
import base64
from typing import Optional, Union, Tuple

try:
    import qrcode
    from qrcode.image.styledpil import StyledPilImage
    from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
    from qrcode.image.styles.colormasks import RadialGradiantColorMask
    from PIL import Image, ImageDraw, ImageFont
    QRCODE_AVAILABLE = True
except ImportError:
    QRCODE_AVAILABLE = False


class 二维码生成器:
    """二维码生成器类，用于生成和保存二维码"""
    
    @staticmethod
    def 检查依赖() -> bool:
        """
        检查是否安装了qrcode库
        
        返回:
            是否可用
        """
        return QRCODE_AVAILABLE
    
    @staticmethod
    def 安装依赖提示() -> str:
        """
        返回安装依赖的提示信息
        
        返回:
            安装提示字符串
        """
        return "请安装qrcode和pillow库以启用二维码功能：\npip install qrcode[pil] pillow"
    
    @staticmethod
    def 生成二维码(数据: str, 文件路径: Optional[str] = None, 
              标题: Optional[str] = None, 
              错误纠正级别: str = 'H', 
              盒子大小: int = 10, 
              边框大小: int = 4,
              样式化: bool = True) -> Union[str, bytes, None]:
        """
        生成二维码
        
        参数:
            数据: 要编码的数据
            文件路径: 保存二维码的文件路径，如果为None则返回二维码图像数据
            标题: 二维码上方的标题文本，如果为None则不添加标题
            错误纠正级别: 错误纠正级别 (L:7%, M:15%, Q:25%, H:30%)
            盒子大小: 二维码中每个小方块的像素大小
            边框大小: 二维码周围的边框大小
            样式化: 是否使用样式化的二维码
            
        返回:
            如果文件路径为None，则返回二维码图像的base64编码或字节数据
            如果文件路径不为None，则返回保存的文件路径
        """
        if not QRCODE_AVAILABLE:
            print(f"错误: {二维码生成器.安装依赖提示()}")
            return None
        
        # 创建QR码实例
        qr = qrcode.QRCode(
            version=None,  # 自动确定版本
            error_correction=getattr(qrcode.constants, f'ERROR_CORRECT_{错误纠正级别}'),
            box_size=盒子大小,
            border=边框大小,
        )
        
        # 添加数据
        qr.add_data(数据)
        qr.make(fit=True)
        
        # 创建图像
        if 样式化:
            try:
                img = qr.make_image(
                    image_factory=StyledPilImage,
                    module_drawer=RoundedModuleDrawer(),
                    color_mask=RadialGradiantColorMask(
                        center_color=(0, 0, 0),
                        edge_color=(50, 50, 50),
                    )
                )
            except Exception:
                # 如果样式化失败，回退到标准图像
                img = qr.make_image(fill_color="black", back_color="white")
        else:
            img = qr.make_image(fill_color="black", back_color="white")
        
        # 如果有标题，添加标题
        if 标题:
            # 创建一个新的白色背景图像，高度增加以容纳标题
            标题高度 = 40  # 标题区域高度
            新图像 = Image.new('RGB', (img.width, img.height + 标题高度), color='white')
            
            # 将二维码图像粘贴到新图像的底部
            新图像.paste(img, (0, 标题高度))
            
            # 添加标题文本
            draw = ImageDraw.Draw(新图像)
            
            # 尝试加载字体，如果失败则使用默认字体
            字体 = None
            try:
                # 尝试使用系统字体
                字体路径 = ""
                if os.name == 'nt':  # Windows
                    字体路径 = "C:\\Windows\\Fonts\\simhei.ttf"
                elif os.name == 'posix':  # macOS/Linux
                    if os.path.exists("/System/Library/Fonts/PingFang.ttc"):
                        字体路径 = "/System/Library/Fonts/PingFang.ttc"
                    elif os.path.exists("/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"):
                        字体路径 = "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"
                
                if 字体路径 and os.path.exists(字体路径):
                    字体 = ImageFont.truetype(字体路径, 20)
            except Exception:
                pass
            
            # 计算文本位置以居中显示
            文本宽度 = draw.textlength(标题, font=字体) if 字体 else len(标题) * 10
            文本位置 = ((新图像.width - 文本宽度) // 2, 10)
            
            # 绘制文本
            draw.text(文本位置, 标题, fill="black", font=字体)
            
            img = 新图像
        
        # 保存或返回图像
        if 文件路径:
            img.save(文件路径)
            return 文件路径
        else:
            # 返回图像数据
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            return base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
    
    @staticmethod
    def 生成助记词二维码(助记词: str, 文件路径: Optional[str] = None) -> Union[str, bytes, None]:
        """
        为助记词生成二维码
        
        参数:
            助记词: 助记词字符串
            文件路径: 保存二维码的文件路径，如果为None则返回二维码图像数据
            
        返回:
            如果文件路径为None，则返回二维码图像的base64编码
            如果文件路径不为None，则返回保存的文件路径
        """
        return 二维码生成器.生成二维码(
            数据=助记词,
            文件路径=文件路径,
            标题="钱包助记词",
            错误纠正级别='H',  # 使用最高级别的错误纠正
            盒子大小=10,
            边框大小=4,
            样式化=True
        )
    
    @staticmethod
    def 生成种子二维码(种子: bytes, 文件路径: Optional[str] = None) -> Union[str, bytes, None]:
        """
        为种子生成二维码
        
        参数:
            种子: 种子字节
            文件路径: 保存二维码的文件路径，如果为None则返回二维码图像数据
            
        返回:
            如果文件路径为None，则返回二维码图像的base64编码
            如果文件路径不为None，则返回保存的文件路径
        """
        种子十六进制 = 种子.hex()
        return 二维码生成器.生成二维码(
            数据=种子十六进制,
            文件路径=文件路径,
            标题="钱包种子(十六进制)",
            错误纠正级别='H',  # 使用最高级别的错误纠正
            盒子大小=6,  # 种子较长，使用较小的盒子大小
            边框大小=4,
            样式化=True
        )
    
    @staticmethod
    def 显示二维码安全提示() -> str:
        """
        返回关于二维码安全性的提示
        
        返回:
            安全提示字符串
        """
        return """
===== 二维码安全提示 =====

1. 二维码包含您的助记词或种子，任何扫描它的人都能获取您的加密资产
2. 请将二维码保存在安全的地方，不要分享或上传到网络
3. 如果您打印二维码，请确保打印机没有连接到互联网或不会保存打印历史
4. 考虑使用密码短语(passphrase)增加额外的安全层
5. 二维码是备份的便捷方式，但不应该是您唯一的备份方式
"""


# 测试代码
if __name__ == "__main__":
    if 二维码生成器.检查依赖():
        测试助记词 = "apple banana cherry dog elephant frog gold hotel ice jungle kite lion monkey"
        二维码路径 = 二维码生成器.生成助记词二维码(测试助记词, "test_qrcode.png")
        print(f"二维码已保存到: {二维码路径}")
        print(二维码生成器.显示二维码安全提示())
    else:
        print(二维码生成器.安装依赖提示())