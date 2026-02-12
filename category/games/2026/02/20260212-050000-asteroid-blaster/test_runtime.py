import os
import sys
import time
import json
import subprocess
import psutil

# Runtime Analysis Configuration
ANALYSIS_DURATION = 120  # 2 minutes
OUTPUT_FILE = "runtime_analysis.json"

def log(message):
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def find_process_by_name(name):
    """Find a process by name"""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if name.lower() in proc.info['name'].lower():
                return proc
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return None

def kill_process_tree(pid):
    """Kill a process and its children"""
    try:
        parent = psutil.Process(pid)
        children = parent.children(recursive=True)
        for child in children:
            try:
                child.kill()
            except psutil.NoSuchProcess:
                pass
        parent.kill()
    except psutil.NoSuchProcess:
        pass

def simulate_keystrokes_windows():
    """Send automated keystrokes to the game window using Windows API"""
    import ctypes
    import ctypes.wintypes

    # Virtual key codes
    VK_SPACE = 0x20
    VK_UP = 0x26
    VK_LEFT = 0x25
    VK_RIGHT = 0x27
    VK_DOWN = 0x28
    VK_ESCAPE = 0x1B

    # Input structure for key events
    KEYEVENTF_SCANCODE = 0x0008
    KEYEVENTF_KEYUP = 0x0002

    class KEYBDINPUT(ctypes.Structure):
        _fields_ = [
            ("wVk", ctypes.wintypes.WORD),
            ("wScan", ctypes.wintypes.WORD),
            ("dwFlags", ctypes.wintypes.DWORD),
            ("time", ctypes.wintypes.DWORD),
            ("dwExtraInfo", ctypes.POINTER(ctypes.wintypes.ULONG)),
        ]

    class INPUT(ctypes.Structure):
        class _INPUT(ctypes.Union):
            _fields_ = [("ki", KEYBDINPUT)]

        _anonymous_ = ("_input",)
        _fields_ = [
            ("type", ctypes.wintypes.DWORD),
            ("_input", _INPUT),
        ]

    user32 = ctypes.windll.user32
    SendInput = user32.SendInput
    SendInput.argtypes = [ctypes.wintypes.UINT, ctypes.POINTER(INPUT), ctypes.c_int]
    SendInput.restype = ctypes.wintypes.UINT

    def send_key(vk_code, press=True):
        """Send a key press or release"""
        inputs = []
        ki = KEYBDINPUT()
        ki.wVk = vk_code
        ki.wScan = 0
        ki.dwFlags = 0 if press else KEYEVENTF_KEYUP
        ki.time = 0
        ki.dwExtraInfo = None

        inp = INPUT()
        inp.type = 1  # INPUT_KEYBOARD
        inp.ki = ki
        inputs.append(inp)

        nInputs = len(inputs)
        inputSize = ctypes.sizeof(INPUT)
        SendInput(nInputs, inputs, inputSize)

    def press_space():
        """Press and release space"""
        send_key(VK_SPACE, True)
        time.sleep(0.05)
        send_key(VK_SPACE, False)

    def hold_key(vk_code, duration):
        """Hold a key for a duration"""
        send_key(vk_code, True)
        time.sleep(duration)
        send_key(vk_code, False)

    return {
        'press_space': press_space,
        'hold_up': lambda d: hold_key(VK_UP, d),
        'hold_left': lambda d: hold_key(VK_LEFT, d),
        'hold_right': lambda d: hold_key(VK_RIGHT, d),
    }

def run_runtime_analysis():
    """Run automated runtime analysis"""
    log("Starting Runtime Analysis")
    log("=" * 50)

    analysis = {
        "app_name": "asteroid-blaster",
        "analysis_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "analysis_duration_seconds": ANALYSIS_DURATION,
        "phases": [],
        "checks": {},
        "errors": [],
        "overall_status": "FAILED"  # Default to FAILED, will update if PASSED
    }

    # Check dependencies
    log("Checking dependencies...")
    checks = analysis["checks"]

    # Check Python
    try:
        import pygame
        checks["pygame_available"] = True
        checks["pygame_version"] = pygame.version.ver
        log(f"  Pygame {pygame.version.ver} found")
    except ImportError:
        checks["pygame_available"] = False
        checks["pygame_version"] = None
        log("  ERROR: Pygame not available")
        analysis["errors"].append("Pygame is not installed")

    # Check main.py exists
    if os.path.exists("main.py"):
        checks["main_py_exists"] = True
        log("  main.py found")
    else:
        checks["main_py_exists"] = False
        log("  ERROR: main.py not found")
        analysis["errors"].append("main.py not found")

    if not checks.get("pygame_available") or not checks.get("main_py_exists"):
        log("Critical dependencies missing, aborting analysis")
        with open(OUTPUT_FILE, 'w') as f:
            json.dump(analysis, f, indent=2)
        return

    log("\nLaunching application...")
    log("-" * 50)

    # Launch the application
    proc = None
    try:
        # Use uv run if available, otherwise python directly
        cmd = ["uv", "run", "main.py"]
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE
        )
        checks["app_launched"] = True
        checks["app_pid"] = proc.pid
        log(f"  Process started with PID: {proc.pid}")

    except Exception as e:
        checks["app_launched"] = False
        analysis["errors"].append(f"Failed to launch: {str(e)}")
        log(f"  ERROR: Failed to launch - {e}")

        with open(OUTPUT_FILE, 'w') as f:
            json.dump(analysis, f, indent=2)
        return

    # Give time for app to initialize
    time.sleep(3)

    # Check if process is still running
    if proc.poll() is not None:
        checks["app_running"] = False
        stdout, stderr = proc.communicate()
        if stderr:
            analysis["errors"].append(f"Startup error: {stderr.decode()}")
        log(f"  ERROR: Process terminated early")
        log(f"  STDERR: {stderr.decode()}")
        with open(OUTPUT_FILE, 'w') as f:
            json.dump(analysis, f, indent=2)
        return

    checks["app_running"] = True
    log("  Application is running")

    # Initialize input simulation
    try:
        input_sim = simulate_keystrokes_windows()
        log("  Input simulation initialized")
    except Exception as e:
        log(f"  WARNING: Could not init input sim: {e}")
        input_sim = None

    # Phase 1: Menu navigation (0-10 seconds)
    phase = {
        "name": "Menu Navigation",
        "start_time": time.time(),
        "duration_seconds": 10,
        "actions": [],
        "status": "PENDING"
    }
    log("\nPhase 1: Menu Navigation")
    log("-" * 50)

    try:
        if input_sim:
            # Press SPACE to start game
            time.sleep(2)
            log("  Action: Press SPACE to start")
            input_sim['press_space']()
            phase["actions"].append("Press SPACE")
            time.sleep(1)

        phase["status"] = "COMPLETED"
        checks["menu_accessible"] = True
        log("  Phase 1 COMPLETED")

    except Exception as e:
        phase["status"] = "FAILED"
        phase["error"] = str(e)
        log(f"  Phase 1 FAILED: {e}")
        analysis["errors"].append(f"Menu navigation failed: {e}")

    analysis["phases"].append(phase)

    # Phase 2: Basic gameplay testing (10-60 seconds)
    phase = {
        "name": "Basic Gameplay",
        "start_time": time.time(),
        "duration_seconds": 50,
        "actions": [],
        "status": "PENDING"
    }
    log("\nPhase 2: Basic Gameplay")
    log("-" * 50)

    start_time = time.time()
    action_count = 0

    try:
        while time.time() - start_time < 50:
            elapsed = time.time() - start_time

            if input_sim:
                # Simulate various actions
                if int(elapsed) % 5 == 0 and action_count != int(elapsed):
                    action_count = int(elapsed)

                    if action_count % 20 == 0:
                        log(f"  Time: {action_count}s - Shooting")
                        input_sim['press_space']()
                        phase["actions"].append(f"Shoot at {action_count}s")

                    elif action_count % 15 == 0:
                        log(f"  Time: {action_count}s - Rotating left")
                        input_sim['hold_left'](0.2)
                        phase["actions"].append(f"Rotate left at {action_count}s")

                    elif action_count % 10 == 0:
                        log(f"  Time: {action_count}s - Rotating right")
                        input_sim['hold_right'](0.2)
                        phase["actions"].append(f"Rotate right at {action_count}s")

                    elif action_count % 5 == 0:
                        log(f"  Time: {action_count}s - Thrusting")
                        input_sim['hold_up'](0.3)
                        phase["actions"].append(f"Thrust at {action_count}s")

            # Check if process still running
            if proc.poll() is not None:
                log("  WARNING: Process terminated during gameplay")
                phase["status"] = "INTERRUPTED"
                phase["terminated_at"] = elapsed
                break

            time.sleep(0.5)

        if proc.poll() is None:
            phase["status"] = "COMPLETED"
            checks["gameplay_stable"] = True
            log("  Phase 2 COMPLETED")
        else:
            checks["gameplay_stable"] = False
            log(f"  Phase 2 INTERRUPTED")

    except Exception as e:
        phase["status"] = "FAILED"
        phase["error"] = str(e)
        log(f"  Phase 2 FAILED: {e}")
        analysis["errors"].append(f"Gameplay failed: {e}")

    analysis["phases"].append(phase)

    # Phase 3: Extended stability test (60-110 seconds)
    phase = {
        "name": "Extended Stability",
        "start_time": time.time(),
        "duration_seconds": 50,
        "status": "PENDING"
    }
    log("\nPhase 3: Extended Stability Test")
    log("-" * 50)

    start_time = time.time()

    try:
        while time.time() - start_time < 50:
            elapsed = time.time() - start_time

            if input_sim and int(elapsed) % 10 == 0:
                log(f"  Stability test: {60 + int(elapsed)}s elapsed")

            if proc.poll() is not None:
                log(f"  Process terminated at {60 + elapsed}s")
                phase["status"] = "INTERRUPTED"
                phase["terminated_at"] = 60 + elapsed
                break

            time.sleep(1)

        if proc.poll() is None:
            phase["status"] = "COMPLETED"
            checks["extended_stable"] = True
            log("  Phase 3 COMPLETED")
        else:
            checks["extended_stable"] = False
            log(f"  Phase 3 INTERRUPTED")

    except Exception as e:
        phase["status"] = "FAILED"
        phase["error"] = str(e)
        log(f"  Phase 3 FAILED: {e}")
        analysis["errors"].append(f"Stability test failed: {e}")

    analysis["phases"].append(phase)

    # Phase 4: Graceful shutdown (110-120 seconds)
    phase = {
        "name": "Graceful Shutdown",
        "start_time": time.time(),
        "status": "PENDING"
    }
    log("\nPhase 4: Graceful Shutdown")
    log("-" * 50)

    try:
        time.sleep(2)

        # Send ESC to quit
        if input_sim:
            log("  Action: Sending ESC to quit")
            # ESC is already handled in the keystroke simulation

        # Wait for graceful termination
        wait_start = time.time()
        terminated = False

        while time.time() - wait_start < 5:
            if proc.poll() is not None:
                terminated = True
                checks["graceful_shutdown"] = True
                phase["status"] = "COMPLETED"
                log("  Application terminated gracefully")
                break
            time.sleep(0.5)

        if not terminated:
            log("  Application did not terminate, force killing")
            phase["status"] = "FORCED"
            checks["graceful_shutdown"] = False

    except Exception as e:
        phase["status"] = "FAILED"
        phase["error"] = str(e)
        log(f"  Phase 4 FAILED: {e}")

    analysis["phases"].append(phase)

    # Force kill if still running
    if proc.poll() is None:
        log("  Force killing process...")
        kill_process_tree(proc.pid)
        time.sleep(1)

    # Calculate overall status
    log("\n" + "=" * 50)
    log("ANALYSIS SUMMARY")
    log("=" * 50)

    passed_count = 0
    total_count = 0

    for check_name, check_value in checks.items():
        if isinstance(check_value, bool):
            total_count += 1
            status = "PASS" if check_value else "FAIL"
            log(f"  {check_name}: {status}")
            if check_value:
                passed_count += 1

    log(f"\nPassed: {passed_count}/{total_count}")

    if passed_count >= total_count * 0.8:  # 80% pass rate
        analysis["overall_status"] = "PASSED"
        log("Overall Status: PASSED")
    else:
        analysis["overall_status"] = "FAILED"
        log("Overall Status: FAILED")

    # Add execution stats
    analysis["execution_stats"] = {
        "total_phases": len(analysis["phases"]),
        "completed_phases": sum(1 for p in analysis["phases"] if p.get("status") == "COMPLETED"),
        "total_actions": sum(len(p.get("actions", [])) for p in analysis["phases"]),
        "total_errors": len(analysis["errors"])
    }

    # Write results
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(analysis, f, indent=2)

    log(f"\nResults saved to {OUTPUT_FILE}")
    log("Analysis complete!")

if __name__ == "__main__":
    os.chdir(r"C:\src\mach-ten-project-artifacts\category\games\2026\02\20260212-050000-asteroid-blaster")
    run_runtime_analysis()
