# smart-file-orchestrator
A lightweight Python background automation tool for secure system-level file orchestration and management.
# Smart File & Asset Orchestrator 🚀

A lightweight, production-ready Python automation tool designed to manage, filter, and clean up messy corporate directories and digital workspaces without dragging down operating system performance.

## 🎯 The Business Case
Digital marketing agencies, media hubs, and performance teams drown in gigabytes of daily assets (videos, banners, briefs, and logs). Standard automation scripts often lock up the system UI or crash due to Windows permission deadlocks when dealing with massive folders. 

This orchestrator runs entirely in the background, bypasses UI layers, and safely handles OS-level constraints to keep infrastructure stable.

---

## ✨ Key Features
* **Zero Dependencies:** Built purely on top of the Python Standard Library (`subprocess`, `json`, `logging`, `argparse`). Runs out of the box.
* **OS-Level Integrity:** Uses native **Windows Management Instrumentation (WMI)** querying to process environment variables and paths reliably.
* **Built-in System Protection:** Implements a strict `PROTECTED_FOLDERS` guardrail (skips critical directories like `System Volume Information`, `Program Files`, and `$Recycle.Bin`) to eliminate accidental OS damage.
* **Global Disk Discovery:** Includes an `--all` flag to automatically map, scan, and process all active logical drives connected to the workstation.
* **Production Logging:** Full UTF-8 structured logging traps access permission loops (`PermissionError`) and target path collisions without breaking the core loop.

---

## 🛠️ Architecture & Core Logic

The script splits its workload into three decoupled phases:
1.  **System Mapping:** Safely fetches active paths via CLI/WMI layers.
2.  **Filter Validation:** Validates the target tree against the protection matrix.
3.  **Atomic Operations:** Executes file shifts with real-time error trapping.

### 📋 Example Code Snippet (Exception & WMI Handling)

```python
# Minimal core concept used for environment isolation
import subprocess
import sys

def check_system_environment():
    try:
        cmd = ["wmic", "startup", "get", "caption,command", "/format:csv"]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Isolated safe execution environment active.", file=sys.stderr)
        return False