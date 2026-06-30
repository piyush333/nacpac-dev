@echo off
echo ========================================
echo  HandVid - Installation
echo ========================================
echo.

REM Create and activate virtual environment
python -m venv venv
call venv\Scripts\activate.bat

REM Upgrade pip
python -m pip install --upgrade pip

REM Install PyTorch with CUDA (adjust cu121 to your CUDA version if needed)
echo Installing PyTorch with CUDA support...
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

REM Install Segment Anything
pip install git+https://github.com/facebookresearch/segment-anything.git

REM Install remaining requirements
pip install -r requirements.txt

echo.
echo ========================================
echo  Downloading models (first-time only)
echo ========================================
python setup_models.py --sam vit_b

echo.
echo ========================================
echo  Installation complete!
echo  Run: venv\Scripts\activate && python app.py
echo ========================================
pause
