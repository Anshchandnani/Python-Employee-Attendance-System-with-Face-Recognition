import subprocess
import sys
import os


def start_recognition():

    project_root = os.path.dirname(
        os.path.dirname(__file__)
    )

    script = os.path.join(
        project_root,
        "run_recognition.py"
    )

    subprocess.Popen(
        [sys.executable, script],
        cwd=project_root
    )