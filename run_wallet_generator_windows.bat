@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: 设置终端颜色
set "GREEN=[92m"
set "BLUE=[94m"
set "YELLOW=[93m"
set "RED=[91m"
set "NC=[0m"

:: 版本信息
set "VERSION=1.1.0"

:: 清屏
cls

:: 显示欢迎信息
echo %GREEN%================================================%NC%
echo %GREEN%    加密货币钱包助记词生成工具 - Windows版    %NC%
echo %GREEN%================================================%NC%
echo %BLUE%版本: %VERSION%%NC%
echo.
echo %BLUE%该工具可以帮助您生成符合BIP-39标准的加密货币钱包助记词%NC%
echo.

:: 检查更新
:check_update
echo %BLUE%正在检查更新...%NC%

:: 尝试导入版本检查器模块
python -c "import sys; sys.path.insert(0, '.'); try: from utils.version_checker import 版本检查器; 有更新, 版本信息 = 版本检查器.检查更新(); print('UPDATE_AVAILABLE' if 有更新 else 'UP_TO_DATE'); except: print('VERSION_CHECKER_NOT_AVAILABLE')" 2>nul | findstr "UPDATE_AVAILABLE" >nul
if %ERRORLEVEL% EQU 0 (
    echo %YELLOW%发现新版本!%NC%
    
    :: 获取更新信息
    python -c "import sys; sys.path.insert(0, '.'); from utils.version_checker import 版本检查器; 有更新, 版本信息 = 版本检查器.检查更新(); print(版本检查器.格式化更新提示(版本信息))"
    
    echo %YELLOW%是否尝试自动更新? (y/n)%NC%
    set /p "auto_update=>"
    
    if /i "!auto_update!"=="y" (
        echo %BLUE%正在尝试自动更新...%NC%
        
        :: 尝试自动更新
        python -c "import sys; sys.path.insert(0, '.'); from utils.version_checker import 版本检查器; 成功, 信息 = 版本检查器.自动更新(); print('UPDATE_SUCCESS' if 成功 else 'UPDATE_FAILED'); print(信息)" | findstr "UPDATE_SUCCESS" >nul
        if %ERRORLEVEL% EQU 0 (
            echo %GREEN%更新成功!%NC%
            echo %YELLOW%请重新启动程序以应用更新。%NC%
            echo %YELLOW%按任意键退出...%NC%
            pause >nul
            exit /b 0
        ) else (
            echo %RED%自动更新失败。%NC%
            echo %YELLOW%请访问 https://github.com/dodo258/crypto-wallet-generator 手动更新。%NC%
        )
    )
) else (
    python -c "import sys; sys.path.insert(0, '.'); try: from utils.version_checker import 版本检查器; print('VERSION_CHECKER_AVAILABLE'); except: print('VERSION_CHECKER_NOT_AVAILABLE')" 2>nul | findstr "VERSION_CHECKER_AVAILABLE" >nul
    if %ERRORLEVEL% EQU 0 (
        echo %GREEN%已经是最新版本。%NC%
    ) else (
        echo %YELLOW%版本检查器不可用，跳过更新检查。%NC%
    )
)

:: 检查Python是否安装
:check_python
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo %RED%错误: 未找到Python。请先安装Python后再运行此脚本。%NC%
    echo 您可以从 https://www.python.org/downloads/ 下载并安装Python。
    echo.
    echo %YELLOW%按任意键退出...%NC%
    pause >nul
    exit /b 1
)

:: 检查Python版本
for /f "tokens=2" %%a in ('python --version 2^>^&1') do set "python_version=%%a"
for /f "tokens=1,2 delims=." %%a in ("%python_version%") do (
    set "python_major=%%a"
    set "python_minor=%%b"
)

if %python_major% LSS 3 (
    echo %RED%警告: 检测到Python版本 %python_version%%NC%
    echo %RED%此工具需要Python 3.7或更高版本。%NC%
    echo %YELLOW%是否继续? (y/n)%NC%
    set /p "continue_anyway=>"
    
    if /i NOT "!continue_anyway!"=="y" (
        echo %YELLOW%按任意键退出...%NC%
        pause >nul
        exit /b 1
    )
) else if %python_major% EQU 3 if %python_minor% LSS 7 (
    echo %RED%警告: 检测到Python版本 %python_version%%NC%
    echo %RED%此工具需要Python 3.7或更高版本。%NC%
    echo %YELLOW%是否继续? (y/n)%NC%
    set /p "continue_anyway=>"
    
    if /i NOT "!continue_anyway!"=="y" (
        echo %YELLOW%按任意键退出...%NC%
        pause >nul
        exit /b 1
    )
) else (
    echo %GREEN%检测到Python版本 %python_version%%NC%
)

:: 检查依赖库是否安装
:check_dependencies
set "req_file=%~1"
set "missing_deps=0"
set "install_missing=0"

echo %BLUE%正在检查依赖库...%NC%

:: 尝试使用依赖管理器
python -c "import sys; sys.path.insert(0, '.'); try: from utils.dependency_manager import 依赖管理器; print('DEPENDENCY_MANAGER_AVAILABLE'); except: print('DEPENDENCY_MANAGER_NOT_AVAILABLE')" 2>nul | findstr "DEPENDENCY_MANAGER_AVAILABLE" >nul
if %ERRORLEVEL% EQU 0 (
    echo %GREEN%使用依赖管理器检查依赖...%NC%
    
    :: 显示依赖状态
    python -c "import sys; sys.path.insert(0, '.'); from utils.dependency_manager import 依赖管理器; print(依赖管理器.显示依赖状态())"
    
    :: 询问是否安装缺失依赖
    echo %YELLOW%是否自动安装缺失的依赖? (y/n)%NC%
    set /p "install_deps=>"
    
    if /i "!install_deps!"=="y" (
        echo %BLUE%正在安装依赖...%NC%
        
        :: 安装依赖
        if "%req_file%"=="requirements.txt" (
            python -c "import sys; sys.path.insert(0, '.'); from utils.dependency_manager import 依赖管理器; 依赖管理器.安装所有基础依赖()"
        ) else if "%req_file%"=="requirements_secure.txt" (
            python -c "import sys; sys.path.insert(0, '.'); from utils.dependency_manager import 依赖管理器; 依赖管理器.安装所有依赖()"
        ) else (
            python -c "import sys; sys.path.insert(0, '.'); from utils.dependency_manager import 依赖管理器; 依赖管理器.从文件安装依赖('%req_file%')"
        )
        
        set "install_missing=1"
        echo %GREEN%依赖安装完成！%NC%
    ) else (
        echo %RED%警告: 缺少必要的依赖库，程序可能无法正常运行。%NC%
        echo %YELLOW%按任意键继续...%NC%
        pause >nul
    )
) else (
    :: 回退到传统方式检查依赖
    echo %YELLOW%依赖管理器不可用，使用传统方式检查依赖...%NC%
    
    :: 读取依赖文件中的每一行
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
    if !missing_deps! EQU 1 (
        echo.
        echo %YELLOW%检测到缺少依赖库。是否要自动安装？(y/n)%NC%
        set /p "install_deps=>"
        
        if /i "!install_deps!"=="y" (
            echo %BLUE%正在安装依赖库...%NC%
            pip install -r "%req_file%"
            set "install_missing=1"
            echo %GREEN%依赖库安装完成！%NC%
        ) else (
            echo %RED%警告: 缺少必要的依赖库，程序可能无法正常运行。%NC%
            echo %YELLOW%按任意键继续...%NC%
            pause >nul
        )
    ) else (
        echo %GREEN%所有依赖库已安装！%NC%
    )
)

exit /b %install_missing%

:: 检查系统环境
:check_system
echo %BLUE%正在检查系统环境...%NC%

:: 检查操作系统
for /f "tokens=*" %%a in ('ver') do set "os_version=%%a"
echo %GREEN%操作系统: %os_version%%NC%

:: 检查处理器架构
for /f "tokens=2 delims=:" %%a in ('wmic os get osarchitecture ^| findstr bit') do set "arch=%%a"
echo %GREEN%处理器架构: %arch%%NC%

:: 检查可用内存
for /f "tokens=4" %%a in ('wmic ComputerSystem get TotalPhysicalMemory ^| findstr [0-9]') do set "total_mem=%%a"
set /a "total_mem_mb=%total_mem% / 1024 / 1024"
echo %GREEN%系统内存: %total_mem_mb% MB%NC%

:: 检查磁盘空间
for /f "tokens=3" %%a in ('dir /-c . ^| findstr "bytes free"') do set "free_space=%%a"
echo %GREEN%可用磁盘空间: %free_space% bytes%NC%

:: 检查网络连接
echo %BLUE%正在检查网络连接...%NC%
ping -n 1 google.com >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo %GREEN%网络连接: 可用%NC%
    
    :: 检查更新
    call :check_update
) else (
    ping -n 1 baidu.com >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo %GREEN%网络连接: 可用%NC%
        
        :: 检查更新
        call :check_update
    ) else (
        echo %YELLOW%网络连接: 不可用%NC%
        echo %YELLOW%无法检查更新。%NC%
    )
)

goto :eof

:: 主菜单
:show_menu
echo.
echo %BLUE%请选择要使用的版本:%NC%
echo.
echo %YELLOW%1. 基础版本%NC% - 简单的命令行工具，支持基本的助记词生成功能 %RED%(建议只生成一次性钱包使用)%NC%
echo %YELLOW%2. 高安全标准版本%NC% - 提供多源熵、内存安全处理、SLIP-39分割备份等高级安全特性
echo %YELLOW%3. 安装依赖%NC% - 安装运行工具所需的依赖库
echo %YELLOW%4. 检查系统环境%NC% - 检查系统环境并诊断问题
echo %YELLOW%5. 退出%NC%
echo %YELLOW%0. 返回上一步%NC%
echo.
echo %BLUE%请输入选项 (0-5):%NC%
set /p "choice=>"

if "%choice%"=="0" (
    :: 返回上一步，重新显示菜单
    cls
    echo %GREEN%================================================%NC%
    echo %GREEN%    加密货币钱包助记词生成工具 - Windows版    %NC%
    echo %GREEN%================================================%NC%
    echo %BLUE%版本: %VERSION%%NC%
    echo.
    echo %BLUE%该工具可以帮助您生成符合BIP-39标准的加密货币钱包助记词%NC%
    echo.
    goto :show_menu
) else if "%choice%"=="1" (
    call :check_dependencies "requirements.txt"
    echo %GREEN%启动基础版本...%NC%
    echo %YELLOW%提示: 使用 'python crypto_wallet_generator.py --help' 查看命令行参数%NC%
    echo.
    python crypto_wallet_generator.py generate
    goto :end
) else if "%choice%"=="2" (
    call :check_dependencies "requirements_secure.txt"
    echo %GREEN%启动高安全标准版本...%NC%
    python crypto_wallet_secure_optimized.py
    goto :end
) else if "%choice%"=="3" (
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
) else if "%choice%"=="4" (
    call :check_system
    echo %YELLOW%按回车键返回主菜单...%NC%
    pause > nul
    goto :show_menu
) else if "%choice%"=="5" (
    echo %GREEN%感谢使用！再见！%NC%
    goto :eof
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

:: 检查Python
call :check_python

:: 运行主菜单
call :show_menu
goto :eof

:: 执行主程序
call :main