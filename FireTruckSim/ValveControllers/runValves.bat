@echo off

set ports=8161 8162 8163 8164 8165

for %%p in (%ports%) do (
	echo %%p > ValveSettings.txt
	python valvecontrol.py %*
)