@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: 设置终端颜色
set "GREEN=[92m"
set "BLUE=[94m"
set "YELLOW=[93m"
set "RED=[91m"
set "NC=[0m"

:: 清屏
cls

:: 显示欢迎信息
echo %GREEN%================================================%NC%
echo %GREEN%    加密货币钱包助记词生成工具 - 依赖安装    %NC%
echo %GREEN%================================================%NC%
echo.

:: 更新pip
echo %BLUE%正在更新pip...%NC%
python -m pip install --upgrade pip
echo %GREEN%pip更新完成%NC%
echo.

:: 安装基础依赖
echo %BLUE%正在安装基础依赖...%NC%
pip install mnemonic click
echo %GREEN%基础依赖安装完成%NC%
echo.

:: 尝试安装高级依赖
echo %BLUE%正在尝试安装高级依赖...%NC%
echo %YELLOW%注意: 某些依赖可能需要编译，如果安装失败可以忽略%NC%
pip install cryptography shamir-mnemonic
echo.

echo %GREEN%安装过程完成！%NC%
echo %YELLOW%如果有依赖安装失败，程序的某些功能可能无法使用。%NC%
echo %YELLOW%但基本功能应该可以正常运行。%NC%
echo.

pause