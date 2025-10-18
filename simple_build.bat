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
echo %GREEN%    加密货币钱包助记词生成工具 - 简易打包    %NC%
echo %GREEN%================================================%NC%
echo.

:: 安装PyInstaller
echo %BLUE%正在安装PyInstaller...%NC%
pip install pyinstaller
echo %GREEN%PyInstaller安装完成%NC%
echo.

:: 打包基础版本
echo %BLUE%正在打包基础版本...%NC%
pyinstaller --onefile --name=crypto_wallet_generator crypto_wallet_generator.py
echo %GREEN%基础版本打包完成%NC%
echo.

:: 打包高安全标准版本
echo %BLUE%正在打包高安全标准版本...%NC%
pyinstaller --onefile --name=crypto_wallet_secure crypto_wallet_secure_optimized.py
echo %GREEN%高安全标准版本打包完成%NC%
echo.

:: 创建启动器
echo %BLUE%正在创建启动器...%NC%
(
echo @echo off
echo chcp 65001 ^>nul
echo setlocal enabledelayedexpansion
echo.
echo :: 设置终端颜色
echo set "GREEN=[92m"
echo set "BLUE=[94m"
echo set "YELLOW=[93m"
echo set "RED=[91m"
echo set "NC=[0m"
echo.
echo :: 清屏
echo cls
echo.
echo :: 显示欢迎信息
echo echo %%GREEN%%================================================%%NC%%
echo echo %%GREEN%%    加密货币钱包助记词生成工具 - Windows版    %%NC%%
echo echo %%GREEN%%================================================%%NC%%
echo echo.
echo echo %%BLUE%%请选择要使用的版本:%%NC%%
echo echo.
echo echo %%YELLOW%%1. 基础版本%%NC%% - 简单的命令行工具，支持基本的助记词生成功能 %%RED%%(建议只生成一次性钱包使用^)%%NC%%
echo echo %%YELLOW%%2. 高安全标准版本%%NC%% - 提供多源熵、内存安全处理、SLIP-39分割备份等高级安全特性
echo echo %%YELLOW%%3. 退出%%NC%%
echo echo.
echo echo %%BLUE%%请输入选项 (1-3^):%%NC%%
echo set /p choice=
echo.
echo if "%%choice%%"=="1" ^(
echo     start crypto_wallet_generator.exe
echo ^) else if "%%choice%%"=="2" ^(
echo     start crypto_wallet_secure.exe
echo ^) else if "%%choice%%"=="3" ^(
echo     exit
echo ^) else ^(
echo     echo %%RED%%无效选项，请重新运行程序%%NC%%
echo     pause
echo ^)
) > dist\启动钱包生成工具.bat

echo %GREEN%启动器创建完成%NC%
echo.

echo %GREEN%打包完成！%NC%
echo %YELLOW%可执行文件位于dist目录中。%NC%
echo %YELLOW%请运行'dist\启动钱包生成工具.bat'来启动程序。%NC%
echo.

pause