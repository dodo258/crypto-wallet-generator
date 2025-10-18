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
echo %GREEN%    加密货币钱包助记词生成工具 - Windows版    %NC%
echo %GREEN%================================================%NC%
echo.
echo %BLUE%该工具可以帮助您生成符合BIP-39标准的加密货币钱包助记词%NC%
echo.

:: 检查Python是否安装
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo %RED%错误: 未找到Python。请先安装Python后再运行此脚本。%NC%
    echo 您可以从 https://www.python.org/downloads/ 下载并安装Python。
    echo.
    echo %YELLOW%按任意键退出...%NC%
    pause >nul
    exit /b 1
)

:: 检查依赖库是否安装
:check_dependencies
set "req_file=%~1"
set "missing_deps=0"

echo %BLUE%正在检查依赖库...%NC%

for /f "tokens=1 delims=>=" %%a in (%req_file%) do (
    set "package=%%a"
    set "package=!package: =!"
    
    python -c "import !package!" >nul 2>&1
    if !ERRORLEVEL! NEQ 0 (
        echo %YELLOW%未安装: !package!%NC%
        set "missing_deps=1"
    )
)

:: 如果有缺失的依赖，提示安装
if %missing_deps% EQU 1 (
    echo.
    echo %YELLOW%检测到缺少依赖库。是否要安装？(y/n)%NC%
    set /p "install_deps=>"
    
    if /i "!install_deps!"=="y" (
        echo %BLUE%正在安装依赖库...%NC%
        pip install -r "%req_file%"
        echo %GREEN%依赖库安装完成！%NC%
    ) else (
        echo %RED%警告: 缺少必要的依赖库，程序可能无法正常运行。%NC%
        echo %YELLOW%按任意键继续...%NC%
        pause >nul
    )
) else (
    echo %GREEN%所有依赖库已安装！%NC%
)
goto :eof

:: 主菜单
:show_menu
echo.
echo %BLUE%请选择要使用的版本:%NC%
echo.
echo %YELLOW%1. 基础版本%NC% - 简单的命令行工具，支持基本的助记词生成功能
echo %YELLOW%2. 中文界面版本%NC% - 提供中文交互界面，适合中文用户使用
echo %YELLOW%3. 高安全标准版本%NC% - 提供多源熵、内存安全处理、SLIP-39分割备份等高级安全特性
echo %YELLOW%4. 安装依赖%NC% - 安装运行工具所需的依赖库
echo %YELLOW%5. 退出%NC%
echo.
echo %BLUE%请输入选项 (1-5):%NC%
set /p "choice=>"

if "%choice%"=="1" (
    call :check_dependencies "requirements.txt"
    echo %GREEN%启动基础版本...%NC%
    echo %YELLOW%提示: 使用 'python crypto_wallet_generator.py --help' 查看命令行参数%NC%
    echo.
    python crypto_wallet_generator.py generate
    goto :end
) else if "%choice%"=="2" (
    call :check_dependencies "requirements.txt"
    echo %GREEN%启动中文界面版本...%NC%
    python crypto_wallet_cn_optimized.py
    goto :end
) else if "%choice%"=="3" (
    call :check_dependencies "requirements_secure.txt"
    echo %GREEN%启动高安全标准版本...%NC%
    python crypto_wallet_secure_optimized.py
    goto :end
) else if "%choice%"=="4" (
    echo %BLUE%请选择要安装的依赖:%NC%
    echo %YELLOW%1. 基础版本依赖%NC%
    echo %YELLOW%2. 高安全标准版本依赖%NC%
    echo %YELLOW%3. 全部依赖%NC%
    echo %YELLOW%4. 返回主菜单%NC%
    echo.
    echo %BLUE%请输入选项 (1-4):%NC%
    set /p "dep_choice=>"
    
    if "!dep_choice!"=="1" (
        pip install -r requirements.txt
        echo %GREEN%基础版本依赖安装完成！%NC%
    ) else if "!dep_choice!"=="2" (
        pip install -r requirements_secure.txt
        echo %GREEN%高安全标准版本依赖安装完成！%NC%
    ) else if "!dep_choice!"=="3" (
        pip install -r requirements.txt
        pip install -r requirements_secure.txt
        echo %GREEN%所有依赖安装完成！%NC%
    ) else if "!dep_choice!"=="4" (
        goto :show_menu
    ) else (
        echo %RED%无效选项，请重新选择%NC%
    )
    
    echo %YELLOW%按任意键返回主菜单...%NC%
    pause >nul
    goto :show_menu
) else if "%choice%"=="5" (
    echo %GREEN%感谢使用！再见！%NC%
    exit /b 0
) else (
    echo %RED%无效选项，请重新选择%NC%
    goto :show_menu
)

:end
:: 程序结束后提示
echo.
echo %GREEN%程序已结束。按任意键退出...%NC%
pause >nul
exit /b 0

:: 启动主菜单
:main
call :show_menu
goto :eof

:: 执行主程序
call :main