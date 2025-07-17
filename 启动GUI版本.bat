@echo off
chcp 65001 >nul
echo ========================================
echo 重复文件清理工具 - GUI版本
echo ========================================
echo.

echo 正在检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python环境，请先安装Python
    echo 下载地址: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo Python环境检查通过
echo.

echo 正在检查依赖库...
python -c "import tkinterdnd2" >nul 2>&1
if errorlevel 1 (
    echo 缺少必要的依赖库 tkinterdnd2
    echo 请先运行 "安装依赖.bat" 来安装所需依赖
    echo.
    echo 或手动安装: pip install tkinterdnd2
    echo.
    pause
    exit /b 1
)

echo 依赖库检查通过，正在启动GUI界面...
echo.

cd /d "%~dp0"
python duplicate_finder_gui.py

if errorlevel 1 (
    echo.
    echo 程序运行出现错误，请检查Python环境和依赖库
    echo 如果问题持续，请运行 "安装依赖.bat" 重新安装依赖
    echo.
    pause
)