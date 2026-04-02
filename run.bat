@echo off
echo 1. Running process.py...
python process.py

echo 2. Running time_anomaly_test.py...
python time_anomaly_test.py

echo 3. Generating flow plots...
python plot_flow.py

echo 4. Generating monthly tendency plots...
python plot_tendency.py

echo All tasks finished!
pause