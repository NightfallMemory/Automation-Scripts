:: Title: Demux Dual Audio
:: Description: Script for automatically demuxing dual/tri/infinite audio anime releases keeping only the Japanese audio. DAD = Dual Audio Demuxed.
:: Author: KazuyaShuu
:: Version: 0.1

@echo off
set /A total = 0
for %%a in ("*.mkv") do (
	ffmpeg -i %%a -map 0:v -map 0:a:language:jp -map 0:s -map 0:t -c copy -y %%~na_DAD.mkv
)
pause