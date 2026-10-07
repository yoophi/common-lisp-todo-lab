"""Verify the built executable from an empty working directory (stdlib only)."""
import json
import os
from pathlib import Path
import socket
import sqlite3
import subprocess
import tempfile
import time
import urllib.error
import urllib.request


binary = Path("build/todo-api").resolve()
with tempfile.TemporaryDirectory(prefix="todo-api-service-") as workdir:
    database = Path(workdir) / "nested" / "todos.db"
    for restart in range(2):
        with socket.socket() as listener:
            listener.bind(("127.0.0.1", 0))
            port = listener.getsockname()[1]
        env = dict(os.environ, HOST="127.0.0.1", PORT=str(port), DATABASE_PATH=str(database))
        with tempfile.TemporaryFile(mode="w+") as log:
            process = subprocess.Popen([str(binary)], cwd=workdir, env=env,
                                       stdin=subprocess.DEVNULL, stdout=log,
                                       stderr=subprocess.STDOUT)
            try:
                deadline = time.monotonic() + 30
                while True:
                    try:
                        with urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=1) as response:
                            assert response.status == 200
                            assert response.headers.get_content_type() == "application/json"
                            assert json.load(response) == {"status": "ok"}
                            break
                    except (urllib.error.URLError, TimeoutError):
                        if process.poll() is not None or time.monotonic() >= deadline:
                            log.seek(0)
                            raise AssertionError("Server did not start:\n" + log.read())
                        time.sleep(0.1)
                with sqlite3.connect(database) as connection:
                    if restart == 0:
                        connection.execute("INSERT INTO todos (title) VALUES (?)", ("재시작 검증",))
                    else:
                        assert connection.execute("SELECT title, completed FROM todos").fetchall() == [("재시작 검증", 0)]
            finally:
                process.terminate()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
                    raise AssertionError("SIGTERM did not stop the server")
            assert process.returncode == 0, process.returncode
print("Executable health, DATABASE_PATH, restart persistence and SIGTERM checks passed.")
