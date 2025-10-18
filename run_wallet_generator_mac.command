#!/bin/bash

# 获取脚本所在目录
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# 设置终端颜色
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # 无颜色

# 版本信息
VERSION="1.1.0"

# 清屏
clear

# 显示欢迎信息
echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}    加密货币钱包助记词生成工具 - Mac版    ${NC}"
echo -e "${GREEN}================================================${NC}"
echo -e "${BLUE}版本: ${VERSION}${NC}"
echo ""
echo -e "${BLUE}该工具可以帮助您生成符合BIP-39标准的加密货币钱包助记词${NC}"
echo ""

# 检查更新
check_update() {
    echo -e "${BLUE}正在检查更新...${NC}"
    
    # 尝试导入版本检查器模块
    if python3 -c "import sys; sys.path.insert(0, '.'); try: from utils.version_checker import 版本检查器; 有更新, 版本信息 = 版本检查器.检查更新(); print('UPDATE_AVAILABLE' if 有更新 else 'UP_TO_DATE'); except: print('VERSION_CHECKER_NOT_AVAILABLE')" 2>/dev/null | grep -q "UPDATE_AVAILABLE"; then
        echo -e "${YELLOW}发现新版本!${NC}"
        
        # 获取更新信息
        python3 -c "import sys; sys.path.insert(0, '.'); from utils.version_checker import 版本检查器; 有更新, 版本信息 = 版本检查器.检查更新(); print(版本检查器.格式化更新提示(版本信息))"
        
        echo -e "${YELLOW}是否尝试自动更新? (y/n)${NC}"
        read -p "> " auto_update
        
        if [[ "$auto_update" =~ ^[Yy]$ ]]; then
            echo -e "${BLUE}正在尝试自动更新...${NC}"
            
            # 尝试自动更新
            if python3 -c "import sys; sys.path.insert(0, '.'); from utils.version_checker import 版本检查器; 成功, 信息 = 版本检查器.自动更新(); print('UPDATE_SUCCESS' if 成功 else 'UPDATE_FAILED'); print(信息)" | grep -q "UPDATE_SUCCESS"; then
                echo -e "${GREEN}更新成功!${NC}"
                echo -e "${YELLOW}请重新启动程序以应用更新。${NC}"
                echo -e "${YELLOW}按任意键退出...${NC}"
                read -n 1
                exit 0
            else
                echo -e "${RED}自动更新失败。${NC}"
                echo -e "${YELLOW}请访问 https://github.com/dodo258/crypto-wallet-generator 手动更新。${NC}"
            fi
        fi
    else
        python3 -c "import sys; sys.path.insert(0, '.'); try: from utils.version_checker import 版本检查器; print('VERSION_CHECKER_AVAILABLE'); except: print('VERSION_CHECKER_NOT_AVAILABLE')" 2>/dev/null | grep -q "VERSION_CHECKER_AVAILABLE" > /dev/null
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}已经是最新版本。${NC}"
        else
            echo -e "${YELLOW}版本检查器不可用，跳过更新检查。${NC}"
        fi
    fi
}

# 检查Python是否安装
check_python() {
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}错误: 未找到Python3。请先安装Python3后再运行此脚本。${NC}"
        echo "您可以从 https://www.python.org/downloads/ 下载并安装Python3。"
        echo ""
        echo -e "${YELLOW}按回车键退出...${NC}"
        read
        exit 1
    fi
    
    # 检查Python版本
    python_version=$(python3 --version | awk '{print $2}')
    python_major=$(echo $python_version | cut -d. -f1)
    python_minor=$(echo $python_version | cut -d. -f2)
    
    if [ "$python_major" -lt 3 ] || ([ "$python_major" -eq 3 ] && [ "$python_minor" -lt 7 ]); then
        echo -e "${RED}警告: 检测到Python版本 ${python_version}${NC}"
        echo -e "${RED}此工具需要Python 3.7或更高版本。${NC}"
        echo -e "${YELLOW}是否继续? (y/n)${NC}"
        read -p "> " continue_anyway
        
        if [[ ! "$continue_anyway" =~ ^[Yy]$ ]]; then
            echo -e "${YELLOW}按回车键退出...${NC}"
            read
            exit 1
        fi
    else
        echo -e "${GREEN}检测到Python版本 ${python_version}${NC}"
    fi
}

# 检查权限
check_permissions() {
    echo -e "${BLUE}正在检查权限...${NC}"
    
    # 尝试使用权限管理器
    if python3 -c "import sys; sys.path.insert(0, '.'); try: from utils.permission_manager import 权限管理器; print('PERMISSION_MANAGER_AVAILABLE'); except: print('PERMISSION_MANAGER_NOT_AVAILABLE')" 2>/dev/null | grep -q "PERMISSION_MANAGER_AVAILABLE"; then
        echo -e "${GREEN}使用权限管理器检查权限...${NC}"
        
        # 显示权限状态
        python3 -c "import sys; sys.path.insert(0, '.'); from utils.permission_manager import 权限管理器; print(权限管理器.显示权限状态())"
        
        # 询问是否修复权限问题
        echo -e "${YELLOW}是否自动修复权限问题? (y/n)${NC}"
        read -p "> " fix_permissions
        
        if [[ "$fix_permissions" =~ ^[Yy]$ ]]; then
            echo -e "${BLUE}正在修复权限问题...${NC}"
            
            # 修复权限
            python3 -c "import sys; sys.path.insert(0, '.'); from utils.permission_manager import 权限管理器; 结果 = 权限管理器.检查并修复权限(); print('修复结果:'); [print(f'  - {k}: {\"成功 ✓\" if v else \"失败 ✗\"}') for k, v in 结果.items()]"
            
            echo -e "${GREEN}权限修复完成！${NC}"
        else
            echo -e "${YELLOW}跳过权限修复。${NC}"
        fi
    else
        # 回退到传统方式检查权限
        echo -e "${YELLOW}权限管理器不可用，使用传统方式检查权限...${NC}"
        
        # 检查脚本是否可执行
        for script in crypto_wallet_generator.py crypto_wallet_cn_optimized.py crypto_wallet_secure_optimized.py run_wallet_generator.sh run_wallet_generator_mac.command; do
            if [ -f "$script" ]; then
                if [ ! -x "$script" ]; then
                    echo -e "${YELLOW}脚本 $script 不可执行，尝试添加执行权限...${NC}"
                    chmod +x "$script"
                    if [ -x "$script" ]; then
                        echo -e "${GREEN}已成功添加执行权限${NC}"
                    else
                        echo -e "${RED}无法添加执行权限${NC}"
                    fi
                else
                    echo -e "${GREEN}脚本 $script 已有执行权限${NC}"
                fi
            else
                echo -e "${RED}脚本 $script 不存在${NC}"
            fi
        done
        
        # 检查配置目录
        config_dir="$HOME/.crypto_wallet"
        if [ ! -d "$config_dir" ]; then
            echo -e "${YELLOW}配置目录不存在，尝试创建...${NC}"
            mkdir -p "$config_dir"
            if [ -d "$config_dir" ]; then
                echo -e "${GREEN}配置目录创建成功${NC}"
            else
                echo -e "${RED}无法创建配置目录${NC}"
            fi
        else
            echo -e "${GREEN}配置目录已存在${NC}"
        fi
    fi
    
    # 检查是否有特殊权限需求
    if [ -f "utils/permission_requirements.txt" ]; then
        echo -e "${BLUE}检查特殊权限需求...${NC}"
        while IFS= read -r line || [[ -n "$line" ]]; do
            # 跳过空行和注释
            [[ -z "$line" || "$line" =~ ^#.*$ ]] && continue
            
            # 处理权限需求
            echo -e "${YELLOW}处理权限需求: $line${NC}"
            eval "$line" || echo -e "${RED}无法满足权限需求: $line${NC}"
        done < "utils/permission_requirements.txt"
    fi
}

# 检查依赖库是否安装
check_dependencies() {
    local req_file=$1
    local missing_deps=0
    local install_missing=0
    
    echo -e "${BLUE}正在检查依赖库...${NC}"
    
    # 尝试使用依赖管理器
    if python3 -c "import sys; sys.path.insert(0, '$(pwd)'); try: from utils.dependency_manager import 依赖管理器; print('DEPENDENCY_MANAGER_AVAILABLE'); except Exception as e: print(f'DEPENDENCY_MANAGER_NOT_AVAILABLE: {e}');" 2>/dev/null | grep -q "DEPENDENCY_MANAGER_AVAILABLE"; then
        echo -e "${GREEN}使用依赖管理器检查依赖...${NC}"
        
        # 显示依赖状态
        python3 -c "import sys; sys.path.insert(0, '$(pwd)'); from utils.dependency_manager import 依赖管理器; print(依赖管理器.显示依赖状态())"
        
        # 检查安全必需依赖
        安全依赖已安装=0
        python3 -c "import sys; sys.path.insert(0, '$(pwd)'); from utils.dependency_manager import 依赖管理器; 安全依赖已安装, 缺失安全依赖 = 依赖管理器.检查安全必需依赖(); print('SECURITY_DEPS_INSTALLED' if 安全依赖已安装 else 'SECURITY_DEPS_MISSING'); print(','.join(缺失安全依赖) if not 安全依赖已安装 else '')" > /tmp/security_deps_status
        
        if grep -q "SECURITY_DEPS_MISSING" /tmp/security_deps_status; then
            缺失安全依赖=$(grep -v "SECURITY_DEPS_MISSING" /tmp/security_deps_status)
            echo -e "${RED}警告: 缺少安全必需依赖: ${缺失安全依赖}${NC}"
            echo -e "${RED}这些依赖对于安全操作是必需的。${NC}"
            echo -e "${YELLOW}是否安装安全必需依赖? (y/n)${NC}"
            read -p "> " install_security_deps
            
            if [[ "$install_security_deps" =~ ^[Yy]$ ]]; then
                echo -e "${BLUE}正在安装安全必需依赖...${NC}"
                python3 -c "import sys; sys.path.insert(0, '$(pwd)'); from utils.dependency_manager import 依赖管理器; 依赖管理器.安装安全必需依赖(True)"
                
                # 再次检查安全依赖
                python3 -c "import sys; sys.path.insert(0, '$(pwd)'); from utils.dependency_manager import 依赖管理器; 安全依赖已安装, _ = 依赖管理器.检查安全必需依赖(); print('SECURITY_DEPS_INSTALLED' if 安全依赖已安装 else 'SECURITY_DEPS_STILL_MISSING')" > /tmp/security_deps_status
                
                if grep -q "SECURITY_DEPS_STILL_MISSING" /tmp/security_deps_status; then
                    echo -e "${RED}错误: 无法安装安全必需依赖。${NC}"
                    echo -e "${RED}为了您的安全，程序将退出。${NC}"
                    echo -e "${YELLOW}按回车键退出...${NC}"
                    read
                    exit 1
                else
                    echo -e "${GREEN}安全依赖安装成功！${NC}"
                fi
            else
                echo -e "${RED}警告: 没有安装安全必需依赖，程序可能存在安全风险。${NC}"
                echo -e "${RED}为了您的安全，程序将退出。${NC}"
                echo -e "${YELLOW}按回车键退出...${NC}"
                read
                exit 1
            fi
        fi
        
        # 询问是否安装缺失依赖
        echo -e "${YELLOW}是否自动安装其他缺失的依赖? (y/n)${NC}"
        read -p "> " install_deps
        
        if [[ "$install_deps" =~ ^[Yy]$ ]]; then
            echo -e "${BLUE}正在安装依赖...${NC}"
            
            # 安装依赖
            if [ "$req_file" = "requirements.txt" ]; then
                python3 -c "import sys; sys.path.insert(0, '$(pwd)'); from utils.dependency_manager import 依赖管理器; 依赖管理器.安装所有基础依赖(True)"
            elif [ "$req_file" = "requirements_secure.txt" ]; then
                python3 -c "import sys; sys.path.insert(0, '$(pwd)'); from utils.dependency_manager import 依赖管理器; 依赖管理器.安装所有依赖(True)"
            else
                python3 -c "import sys; sys.path.insert(0, '$(pwd)'); from utils.dependency_manager import 依赖管理器; 依赖管理器.从文件安装依赖('$req_file', True)"
            fi
            
            install_missing=1
            echo -e "${GREEN}依赖安装完成！${NC}"
        else
            echo -e "${YELLOW}跳过安装其他依赖。${NC}"
        fi
    else
        # 回退到传统方式检查依赖
        echo -e "${YELLOW}依赖管理器不可用，使用传统方式检查依赖...${NC}"
        
        # 读取依赖文件中的每一行
        while IFS= read -r line || [[ -n "$line" ]]; do
            # 跳过空行和注释
            [[ -z "$line" || "$line" =~ ^#.*$ ]] && continue
            
            # 提取包名（去掉版本号）
            package=$(echo "$line" | cut -d'>' -f1 | cut -d'=' -f1 | cut -d'<' -f1 | tr -d ' ')
            
            # 检查包是否已安装
            if ! python3 -c "import $package" &> /dev/null; then
                echo -e "${YELLOW}未安装: $package${NC}"
                missing_deps=1
            fi
        done < "$req_file"
        
        # 如果有缺失的依赖，提示安装
        if [ $missing_deps -eq 1 ]; then
            echo ""
            echo -e "${YELLOW}检测到缺少依赖库。是否要自动安装？(y/n)${NC}"
            read -p "> " install_deps
            
            if [[ "$install_deps" =~ ^[Yy]$ ]]; then
                echo -e "${BLUE}正在安装依赖库...${NC}"
                pip3 install -r "$req_file"
                install_missing=1
                echo -e "${GREEN}依赖库安装完成！${NC}"
            else
                echo -e "${RED}警告: 缺少必要的依赖库，程序可能无法正常运行。${NC}"
                echo -e "${YELLOW}按回车键继续...${NC}"
                read
            fi
        else
            echo -e "${GREEN}所有依赖库已安装！${NC}"
        fi
    fi
    
    return $install_missing
}

# 检查系统环境
check_system() {
    echo -e "${BLUE}正在检查系统环境...${NC}"
    
    # 检查操作系统
    os_name=$(uname -s)
    os_version=$(uname -r)
    echo -e "${GREEN}操作系统: ${os_name} ${os_version}${NC}"
    
    # 检查处理器架构
    arch=$(uname -m)
    echo -e "${GREEN}处理器架构: ${arch}${NC}"
    
    # 检查可用内存
    if [ "$os_name" = "Darwin" ]; then
        # macOS
        total_mem=$(sysctl -n hw.memsize)
        total_mem_mb=$((total_mem / 1024 / 1024))
        echo -e "${GREEN}系统内存: ${total_mem_mb} MB${NC}"
    elif [ "$os_name" = "Linux" ]; then
        # Linux
        total_mem=$(grep MemTotal /proc/meminfo | awk '{print $2}')
        total_mem_mb=$((total_mem / 1024))
        echo -e "${GREEN}系统内存: ${total_mem_mb} MB${NC}"
    fi
    
    # 检查磁盘空间
    df_output=$(df -h . | tail -n 1)
    available_space=$(echo $df_output | awk '{print $4}')
    echo -e "${GREEN}可用磁盘空间: ${available_space}${NC}"
    
    # 检查网络连接
    echo -e "${BLUE}正在检查网络连接...${NC}"
    if ping -c 1 google.com &> /dev/null || ping -c 1 baidu.com &> /dev/null; then
        echo -e "${GREEN}网络连接: 可用${NC}"
        
        # 检查更新
        check_update
    else
        echo -e "${YELLOW}网络连接: 不可用${NC}"
        echo -e "${YELLOW}无法检查更新。${NC}"
    fi
}

# 主菜单
show_menu() {
    echo ""
    echo -e "${BLUE}请选择要使用的版本:${NC}"
    echo ""
    echo -e "${YELLOW}1. 基础版本${NC} - 简单的命令行工具，支持基本的助记词生成功能 ${RED}(建议只生成一次性钱包使用)${NC}"
    echo -e "${YELLOW}2. 中文界面版本${NC} - 提供中文交互界面，适合中文用户使用"
    echo -e "${YELLOW}3. 高安全标准版本${NC} - 提供多源熵、内存安全处理、SLIP-39分割备份等高级安全特性"
    echo -e "${YELLOW}4. 安装依赖${NC} - 安装运行工具所需的依赖库"
    echo -e "${YELLOW}5. 检查系统环境${NC} - 检查系统环境并诊断问题"
    echo -e "${YELLOW}6. 检查和修复权限${NC} - 检查和修复文件权限问题"
    echo -e "${YELLOW}7. 退出${NC}"
    echo -e "${YELLOW}0. 返回上一步${NC}"
    echo ""
    echo -e "${BLUE}请输入选项 (0-7):${NC}"
    read -p "> " choice
    
    case $choice in
        0)
            # 返回上一步，重新显示菜单
            clear
            echo -e "${GREEN}================================================${NC}"
            echo -e "${GREEN}    加密货币钱包助记词生成工具 - Mac版    ${NC}"
            echo -e "${GREEN}================================================${NC}"
            echo -e "${BLUE}版本: ${VERSION}${NC}"
            echo ""
            echo -e "${BLUE}该工具可以帮助您生成符合BIP-39标准的加密货币钱包助记词${NC}"
            echo ""
            show_menu
            ;;
        1)
            check_dependencies "requirements.txt"
            echo -e "${GREEN}启动基础版本...${NC}"
            echo -e "${YELLOW}提示: 使用 'python3 crypto_wallet_generator.py --help' 查看命令行参数${NC}"
            echo ""
            python3 crypto_wallet_generator.py generate
            ;;
        2)
            check_dependencies "requirements.txt"
            echo -e "${GREEN}启动中文界面版本...${NC}"
            python3 crypto_wallet_cn_optimized.py
            ;;
        3)
            check_dependencies "requirements_secure.txt"
            echo -e "${GREEN}启动高安全标准版本...${NC}"
            python3 crypto_wallet_secure_optimized.py
            ;;
        4)
            echo -e "${BLUE}请选择要安装的依赖:${NC}"
            echo -e "${YELLOW}1. 基础版本依赖${NC}"
            echo -e "${YELLOW}2. 高安全标准版本依赖${NC}"
            echo -e "${YELLOW}3. 全部依赖${NC}"
            echo -e "${YELLOW}4. 返回主菜单${NC}"
            echo ""
            echo -e "${BLUE}请输入选项 (1-4):${NC}"
            read -p "> " dep_choice
            
            case $dep_choice in
                1)
                    if python3 -c "import sys; sys.path.insert(0, '$(pwd)'); try: from utils.dependency_manager import 依赖管理器; print('DEPENDENCY_MANAGER_AVAILABLE'); except Exception as e: print(f'DEPENDENCY_MANAGER_NOT_AVAILABLE: {e}');" 2>/dev/null | grep -q "DEPENDENCY_MANAGER_AVAILABLE"; then
                        python3 -c "import sys; sys.path.insert(0, '$(pwd)'); from utils.dependency_manager import 依赖管理器; 依赖管理器.安装所有基础依赖(True)"
                    else
                        pip3 install -r requirements.txt
                    fi
                    echo -e "${GREEN}基础版本依赖安装完成！${NC}"
                    ;;
                2)
                    if python3 -c "import sys; sys.path.insert(0, '$(pwd)'); try: from utils.dependency_manager import 依赖管理器; print('DEPENDENCY_MANAGER_AVAILABLE'); except Exception as e: print(f'DEPENDENCY_MANAGER_NOT_AVAILABLE: {e}');" 2>/dev/null | grep -q "DEPENDENCY_MANAGER_AVAILABLE"; then
                        python3 -c "import sys; sys.path.insert(0, '$(pwd)'); from utils.dependency_manager import 依赖管理器; 依赖管理器.安装所有依赖(True)"
                    else
                        pip3 install -r requirements_secure.txt
                    fi
                    echo -e "${GREEN}高安全标准版本依赖安装完成！${NC}"
                    ;;
                3)
                    if python3 -c "import sys; sys.path.insert(0, '$(pwd)'); try: from utils.dependency_manager import 依赖管理器; print('DEPENDENCY_MANAGER_AVAILABLE'); except Exception as e: print(f'DEPENDENCY_MANAGER_NOT_AVAILABLE: {e}');" 2>/dev/null | grep -q "DEPENDENCY_MANAGER_AVAILABLE"; then
                        python3 -c "import sys; sys.path.insert(0, '$(pwd)'); from utils.dependency_manager import 依赖管理器; 依赖管理器.安装所有依赖(True)"
                    else
                        pip3 install -r requirements.txt
                        pip3 install -r requirements_secure.txt
                    fi
                    echo -e "${GREEN}所有依赖安装完成！${NC}"
                    ;;
                4)
                    show_menu
                    return
                    ;;
                *)
                    echo -e "${RED}无效选项，请重新选择${NC}"
                    ;;
            esac
            
            echo -e "${YELLOW}按回车键返回主菜单...${NC}"
            read
            show_menu
            ;;
        5)
            check_system
            echo -e "${YELLOW}按回车键返回主菜单...${NC}"
            read
            show_menu
            ;;
        6)
            check_permissions
            echo -e "${YELLOW}按回车键返回主菜单...${NC}"
            read
            show_menu
            ;;
        7)
            echo -e "${GREEN}感谢使用！再见！${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}无效选项，请重新选择${NC}"
            show_menu
            ;;
    esac
}

# 检查Python
check_python

# 检查权限
check_permissions

# 运行主菜单
show_menu

# 程序结束后提示
echo ""
echo -e "${GREEN}程序已结束。按回车键退出...${NC}"
read
exit 0