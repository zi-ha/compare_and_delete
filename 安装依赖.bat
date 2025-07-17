@echo off
chcp 65001 >nul
echo ========================================
echo 安装GUI版本所需依赖库
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

echo 正在安装tkinterdnd2库（支持拖放功能）...
python -m pip install tkinterdnd2

if errorlevel 1 (
    echo.
    echo 安装失败，尝试使用国内镜像源...
    python -m pip install tkinterdnd2 -i https://pypi.tuna.tsinghua.edu.cn/simple/
    
    if errorlevel 1 (
        echo.
        echo 安装仍然失败，请检查网络连接或手动安装：
        echo pip install tkinterdnd2
        echo.
        pause
        exit /b 1
    )
)

echo.
echo ========================================
echo 依赖库安装完成！
echo ========================================
echo.
echo 现在可以运行GUI版本了：
echo - 双击 "启动GUI版本.bat"
echo - 或运行: python duplicate_finder_gui.py
echo.
pause