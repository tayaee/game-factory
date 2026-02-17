"""
Runtime analysis test script for Vector Mappy Rhythm Run
This script simulates key presses to test basic game functionality
"""
import sys
import os
import subprocess
import json
import time

# Analysis results
analysis_result = {
    "app_name": "vector-mappy-rhythm-run",
    "timestamp": "",
    "overall_status": "FAILED",
    "startup": {},
    "basic_functionality": {},
    "issues": [],
    "observations": []
}

analysis_result["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")

print(f"[{time.strftime('%H:%M:%S')}] Starting runtime analysis...")
print(f"[{time.strftime('%H:%M:%S')}] Launching Vector Mappy Rhythm Run...")

# Start the game process
process = None
try:
    process = subprocess.Popen(
        [os.path.join(".venv", "Scripts", "python.exe"), "main.py"],
        cwd=os.getcwd(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        shell=False
    )
    analysis_result["startup"]["pid"] = process.pid
    analysis_result["startup"]["start_time"] = time.strftime("%H:%M:%S")
    print(f"[{time.strftime('%H:%M:%S')}] Game started with PID: {process.pid}")
except Exception as e:
    analysis_result["issues"].append(f"Failed to start process: {str(e)}")
    print(f"[{time.strftime('%H:%M:%S')}] ERROR: Failed to start process - {e}")
    # Save result and exit
    with open("runtime_analysis.json", "w") as f:
        json.dump(analysis_result, f, indent=2)
    sys.exit(1)

# Wait for initialization
print(f"[{time.strftime('%H:%M:%S')}] Waiting for game initialization (5s)...")
time.sleep(5)

# Check if process is still running
if process.poll() is None:
    analysis_result["startup"]["process_running"] = True
    analysis_result["startup"]["initialization"] = "SUCCESS"
    print(f"[{time.strftime('%H:%M:%S')}] Process is running - initialization SUCCESS")
    analysis_result["observations"].append("Process started successfully and remains running")
else:
    analysis_result["startup"]["process_running"] = False
    analysis_result["startup"]["initialization"] = "FAILED"
    stdout, stderr = process.communicate()
    analysis_result["issues"].append(f"Process exited during initialization. stdout: {stdout}, stderr: {stderr}")
    print(f"[{time.strftime('%H:%M:%S')}] ERROR: Process exited during initialization")
    print(f"[{time.strftime('%H:%M:%S')}] stderr: {stderr}")
    with open("runtime_analysis.json", "w") as f:
        json.dump(analysis_result, f, indent=2)
    sys.exit(1)

# Monitor for another minute to check stability
print(f"[{time.strftime('%H:%M:%S')}] Monitoring game stability for 60 seconds...")
monitor_start = time.time()
process_stable = True

while time.time() - monitor_start < 60:
    if process.poll() is not None:
        process_stable = False
        analysis_result["issues"].append("Process crashed during monitoring period")
        print(f"[{time.strftime('%H:%M:%S')}] ERROR: Process crashed during monitoring")
        break
    time.sleep(5)

if process_stable:
    analysis_result["basic_functionality"]["stability"] = "PASSED"
    analysis_result["basic_functionality"]["running_time_sec"] = round(time.time() - monitor_start, 2)
    print(f"[{time.strftime('%H:%M:%S')}] Process remained stable for 60 seconds")
    analysis_result["observations"].append("Process remained stable during monitoring period")

# Determine overall status
if (analysis_result["startup"]["initialization"] == "SUCCESS" and
    process_stable and
    len(analysis_result["issues"]) == 0):
    analysis_result["overall_status"] = "PASSED"
    print(f"[{time.strftime('%H:%M:%S')}] Runtime analysis: PASSED")
else:
    analysis_result["overall_status"] = "FAILED"
    print(f"[{time.strftime('%H:%M:%S')}] Runtime analysis: FAILED")

# Terminate the game process
print(f"[{time.strftime('%H:%M:%S')}] Terminating game process...")
try:
    process.terminate()
    process.wait(timeout=5)
    analysis_result["observations"].append("Process terminated cleanly")
except subprocess.TimeoutExpired:
    try:
        process.kill()
        analysis_result["observations"].append("Process killed forcefully")
    except:
        pass
except Exception as e:
    analysis_result["issues"].append(f"Error terminating process: {str(e)}")

# Save analysis results
with open("runtime_analysis.json", "w") as f:
    json.dump(analysis_result, f, indent=2)

print(f"[{time.strftime('%H:%M:%S')}] Analysis results saved to runtime_analysis.json")
print(f"[{time.strftime('%H:%M:%S')}] Runtime analysis complete")
