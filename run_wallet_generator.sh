#!/bin/bash

# 设置终端颜色
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # 无颜色

# 清屏
clear

# 显示欢迎信息
echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}    加密货币钱包助记词生成工具 - 启动器    ${NC}"
echo -e "${GREEN}================================================${NC}"
echo ""
echo -e "${BLUE}该工具可以帮助您生成符合BIP-39标准的加密货币钱包助记词${NC}"
echo ""

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}错误: 未找到Python3。请先安装Python3后再运行此脚本。${NC}"
    echo "您可以从 https://www.python.org/downloads/ 下载并安装Python3。"
    echo ""
    echo -e "${YELLOW}按任意键退出...${NC}"
    read -n 1
    exit 1
fi

# 检查依赖库是否安装
check_dependencies() {
    local req_file=$1
    local missing_deps=0
    
    echo -e "${BLUE}正在检查依赖库...${NC}"
    
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
        echo -e "${YELLOW}检测到缺少依赖库。是否要安装？(y/n)${NC}"
        read -p "> " install_deps
        
        if [[ "$install_deps" =~ ^[Yy]$ ]]; then
            echo -e "${BLUE}正在安装依赖库...${NC}"
            pip3 install -r "$req_file"
            echo -e "${GREEN}依赖库安装完成！${NC}"
        else
            echo -e "${RED}警告: 缺少必要的依赖库，程序可能无法正常运行。${NC}"
            echo -e "${YELLOW}按任意键继续...${NC}"
            read -n 1
        fi
    else
        echo -e "${GREEN}所有依赖库已安装！${NC}"
    fi
}

# 主菜单
show_menu() {
    echo ""
    echo -e "${BLUE}请选择要使用的版本:${NC}"
    echo ""
    echo -e "${YELLOW}1. 基础版本${NC} - 简单的命令行工具，支持基本的助记词生成功能"
    echo -e "${YELLOW}2. 中文界面版本${NC} - 提供中文交互界面，适合中文用户使用"
    echo -e "${YELLOW}3. 高安全标准版本${NC} - 提供多源熵、内存安全处理、SLIP-39分割备份等高级安全特性"
    echo -e "${YELLOW}4. 安装依赖${NC} - 安装运行工具所需的依赖库"
    echo -e "${YELLOW}5. 退出${NC}"
    echo ""
    echo -e "${BLUE}请输入选项 (1-5):${NC}"
    read -p "> " choice
    
    case $choice in
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
                    pip3 install -r requirements.txt
                    echo -e "${GREEN}基础版本依赖安装完成！${NC}"
                    ;;
                2)
                    pip3 install -r requirements_secure.txt
                    echo -e "${GREEN}高安全标准版本依赖安装完成！${NC}"
                    ;;
                3)
                    pip3 install -r requirements.txt
                    pip3 install -r requirements_secure.txt
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
            
            echo -e "${YELLOW}按任意键返回主菜单...${NC}"
            read -n 1
            show_menu
            ;;
        5)
            echo -e "${GREEN}感谢使用！再见！${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}无效选项，请重新选择${NC}"
            show_menu
            ;;
    esac
}

# 运行主菜单
show_menu

# 程序结束后提示
echo ""
echo -e "${GREEN}程序已结束。按任意键退出...${NC}"
read -n 1
exit 0