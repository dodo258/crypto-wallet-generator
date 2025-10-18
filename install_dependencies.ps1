# 加密货币钱包助记词生成工具 - 依赖安装脚本
# 版本: 1.0.0

# 设置终端颜色
$GREEN = @{ForegroundColor = "Green"}
$BLUE = @{ForegroundColor = "Cyan"}
$YELLOW = @{ForegroundColor = "Yellow"}
$RED = @{ForegroundColor = "Red"}

# 清屏
Clear-Host

# 显示欢迎信息
Write-Host "================================================" @GREEN
Write-Host "    加密货币钱包助记词生成工具 - 依赖安装    " @GREEN
Write-Host "================================================" @GREEN
Write-Host "版本: 1.0.0" @BLUE
Write-Host ""
Write-Host "该脚本将安装运行加密货币钱包助记词生成工具所需的所有依赖" @BLUE
Write-Host ""

# 检查Python是否安装
function Check-Python {
    try {
        $pythonVersion = (python --version 2>&1)
        if ($pythonVersion -match "Python (\d+)\.(\d+)\.(\d+)") {
            $major = [int]$Matches[1]
            $minor = [int]$Matches[2]
            
            if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 7)) {
                Write-Host "警告: 检测到Python版本 $pythonVersion" @RED
                Write-Host "此工具需要Python 3.7或更高版本。" @RED
                $continue = Read-Host "是否继续? (y/n)"
                if ($continue -ne "y") {
                    exit
                }
            } else {
                Write-Host "检测到Python版本 $pythonVersion" @GREEN
            }
            return $true
        } else {
            throw "无法识别Python版本"
        }
    } catch {
        Write-Host "错误: 未找到Python。请先安装Python后再运行此脚本。" @RED
        Write-Host "您可以从 https://www.python.org/downloads/ 下载并安装Python。"
        Write-Host ""
        Write-Host "按任意键退出..." @YELLOW
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        exit
    }
}

# 检查pip是否安装
function Check-Pip {
    try {
        $pipVersion = (pip --version 2>&1)
        if ($pipVersion -match "pip (\d+)\.(\d+)") {
            Write-Host "检测到pip版本 $pipVersion" @GREEN
            return $true
        } else {
            throw "无法识别pip版本"
        }
    } catch {
        Write-Host "错误: 未找到pip。正在尝试安装..." @YELLOW
        try {
            python -m ensurepip
            python -m pip install --upgrade pip
            Write-Host "pip安装成功！" @GREEN
            return $true
        } catch {
            Write-Host "错误: 无法安装pip。请手动安装pip后再运行此脚本。" @RED
            Write-Host "您可以运行: python -m ensurepip --upgrade" @BLUE
            Write-Host ""
            Write-Host "按任意键退出..." @YELLOW
            $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
            exit
        }
    }
}

# 安装基础依赖
function Install-BasicDependencies {
    Write-Host "正在安装基础依赖..." @BLUE
    try {
        pip install --no-warn-script-location -r requirements.txt
        Write-Host "基础依赖安装完成！" @GREEN
        return $true
    } catch {
        Write-Host "错误: 安装基础依赖时出错。" @RED
        Write-Host $_.Exception.Message
        return $false
    }
}

# 安装高级依赖
function Install-AdvancedDependencies {
    Write-Host "正在安装高级依赖..." @BLUE
    try {
        pip install --no-warn-script-location -r requirements_secure.txt
        Write-Host "高级依赖安装完成！" @GREEN
        return $true
    } catch {
        Write-Host "错误: 安装高级依赖时出错。" @RED
        Write-Host $_.Exception.Message
        return $false
    }
}

# 安装所有依赖
function Install-AllDependencies {
    $basicSuccess = Install-BasicDependencies
    $advancedSuccess = Install-AdvancedDependencies
    
    if ($basicSuccess -and $advancedSuccess) {
        Write-Host "所有依赖安装成功！" @GREEN
        return $true
    } else {
        Write-Host "警告: 部分依赖安装失败。" @YELLOW
        return $false
    }
}

# 主菜单
function Show-Menu {
    Write-Host ""
    Write-Host "请选择要安装的依赖:" @BLUE
    Write-Host ""
    Write-Host "1. 基础版本依赖" @YELLOW -NoNewline
    Write-Host " - 仅安装基本功能所需依赖"
    Write-Host "2. 高安全标准版本依赖" @YELLOW -NoNewline
    Write-Host " - 安装包含SLIP-39等高级功能的依赖"
    Write-Host "3. 全部依赖" @YELLOW -NoNewline
    Write-Host " - 安装所有依赖"
    Write-Host "4. 退出" @YELLOW
    Write-Host ""
    Write-Host "请输入选项 (1-4):" @BLUE
    
    $choice = Read-Host
    
    switch ($choice) {
        "1" {
            Install-BasicDependencies
        }
        "2" {
            Install-AdvancedDependencies
        }
        "3" {
            Install-AllDependencies
        }
        "4" {
            Write-Host "感谢使用！再见！" @GREEN
            exit
        }
        default {
            Write-Host "无效选项，请重新选择" @RED
            Show-Menu
        }
    }
    
    Write-Host ""
    Write-Host "按任意键退出..." @GREEN
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

# 主程序
function Main {
    # 检查Python
    Check-Python
    
    # 检查pip
    Check-Pip
    
    # 显示菜单
    Show-Menu
}

# 执行主程序
Main