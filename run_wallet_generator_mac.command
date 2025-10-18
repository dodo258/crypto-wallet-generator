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