"""
PyInstaller钩子文件，用于确保shamir_mnemonic模块的所有文件都被包含在打包中
"""

from PyInstaller.utils.hooks import collect_all

# 收集shamir_mnemonic模块的所有文件
datas, binaries, hiddenimports = collect_all('shamir_mnemonic')