@echo off

set spath=%~dp0
pushd %spath%

call anaconda_path_cfg.bat
call %anaconda_path%\Scripts\activate.bat %anaconda_path%

call conda activate video_conv
python  %spath%/ui.py 

popd