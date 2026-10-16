#!/usr/bin/env python3
"""
Smart Manufacturing Process Optimization - Local Development Runner
Launches both the Flask AI backend (:5001) and an HTTP frontend server (:8000),
then automatically opens the dashboard in your default browser.
Guarantees clean port binding by auto-terminating any stale processes on 5001/8000.
"""

import os
import sys
import time
import signal
import subprocess
import webbrowser

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(PROJECT_DIR, "backend")


def free_port(port: int):
    """Detect and gracefully terminate any stale process holding the specified port."""
    try:
        output = subprocess.check_output(["lsof", "-ti", f":{port}"], text=True).strip()
        if output:
            for pid_str in output.split():
                pid = int(pid_str)
                if pid != os.getpid():
                    print(f"  [cleanup] Freeing port {port} (killing PID {pid})...")
                    try:
                        os.kill(pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
            time.sleep(0.5)
    except Exception:
        # lsof returns non-zero if no process is listening, which is normal
        pass


def main():
    print("=" * 60)
    print("  🚀 Starting Smart Manufacturing Process Optimization Platform")
    print("=" * 60)

    # 1. Clean up ports 5001 & 8000 to prevent Errno 48 "Address already in use"
    print("\n[1/3] Ensuring ports 5001 and 8000 are clear...")
    free_port(5001)
    free_port(8000)

    # 2. Start Flask AI Backend on Port 5001
    print("[2/3] Launching Flask AI Backend Server on http://127.0.0.1:5001 ...")
    backend_proc = subprocess.Popen(
        [sys.executable, "app.py"],
        cwd=BACKEND_DIR
    )

    time.sleep(2)

    # 3. Start Frontend Server on Port 8000
    print("[3/3] Launching Web Frontend Server on http://127.0.0.1:8000 ...")
    frontend_proc = subprocess.Popen(
        [sys.executable, "-m", "http.server", "8000"],
        cwd=PROJECT_DIR,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    time.sleep(1)

    # Open Dashboard in default browser
    dashboard_url = "http://127.0.0.1:8000/dashboard.html"
    print(f"\n  🌐 Opening Dashboard in browser: {dashboard_url}")
    try:
        webbrowser.open(dashboard_url)
    except Exception:
        pass

    print("\n" + "=" * 60)
    print("  ✅ Platform is Live!")
    print(f"  • Frontend Dashboard : {dashboard_url}")
    print("  • Login Page         : http://127.0.0.1:8000/index.html")
    print("  • Backend REST API   : http://127.0.0.1:5001")
    print("  • OpenAPI 3.0 Spec   : http://127.0.0.1:5001/lld/spec")
    print("=" * 60)
    print("Press Ctrl+C to stop both servers.\n")

    try:
        backend_proc.wait()
    except KeyboardInterrupt:
        print("\nStopping servers...")
        backend_proc.terminate()
        frontend_proc.terminate()
        print("Servers stopped successfully.")


if __name__ == "__main__":
    main()
