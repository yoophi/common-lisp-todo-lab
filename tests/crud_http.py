"""Exercise the real HTTP service and SQLite persistence; Python stdlib only."""
from concurrent.futures import ThreadPoolExecutor
import http.client
import json
import os
from pathlib import Path
import socket
import subprocess
import tempfile
import time
import unittest


class TodoAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.binary = str(Path("build/todo-api").resolve())
        cls.workspace = tempfile.TemporaryDirectory(prefix="todo-crud-")
        cls.addClassCleanup(cls.workspace.cleanup)
        cls.log = tempfile.TemporaryFile(mode="w+")
        cls.addClassCleanup(cls.log.close)
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            cls.port = sock.getsockname()[1]
        cls.env = dict(os.environ, HOST="127.0.0.1", PORT=str(cls.port),
                       DATABASE_PATH=str(Path(cls.workspace.name) / "todos.db"))
        cls.process = None
        cls.addClassCleanup(cls.stop_server)
        cls.start_server()

    @classmethod
    def start_server(cls):
        cls.process = subprocess.Popen([cls.binary], cwd=cls.workspace.name, env=cls.env,
                                       stdin=subprocess.DEVNULL, stdout=cls.log, stderr=cls.log)
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline:
            try:
                if cls.request("GET", "/health")[0] == 200:
                    return
            except OSError:
                pass
            if cls.process.poll() is not None:
                break
            time.sleep(0.1)
        cls.log.seek(0)
        raise AssertionError("Startup failed:\n" + cls.log.read())

    @classmethod
    def stop_server(cls):
        if cls.process and cls.process.poll() is None:
            cls.process.terminate()
            try:
                code = cls.process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                cls.process.kill()
                cls.process.wait()
                raise AssertionError("Server ignored SIGTERM")
            assert code == 0, code

    @classmethod
    def request(cls, method, path, payload=None, *, raw=None, content_type="application/json", chunked=False):
        body = raw if raw is not None else (json.dumps(payload, ensure_ascii=False).encode() if payload is not None else None)
        headers = {"Content-Type": content_type} if body is not None else {}
        connection = http.client.HTTPConnection("127.0.0.1", cls.port, timeout=10)
        try:
            if chunked:
                body = iter([body])
            connection.request(method, path, body, headers, encode_chunked=chunked)
            response = connection.getresponse()
            data = response.read()
            result = json.loads(data) if data else None
            return response.status, dict(response.getheaders()), result
        finally:
            connection.close()

    def setUp(self):
        status, _, rows = self.request("GET", "/todos?limit=100")
        self.assertEqual(status, 200)
        for row in rows:
            self.assertEqual(self.request("DELETE", f'/todos/{row["id"]}')[0], 204)

    def create(self, title="테스트", **fields):
        status, headers, row = self.request("POST", "/todos", dict(title=title, **fields))
        self.assertEqual(status, 201, row)
        self.assertEqual(headers["Location"], f'/todos/{row["id"]}')
        return row

    def assert_error(self, status, method, path, payload=None, **kwargs):
        actual, headers, body = self.request(method, path, payload, **kwargs)
        self.assertEqual(actual, status, body)
        self.assertTrue(headers["Content-Type"].startswith("application/json"))
        self.assertIsInstance(body["error"]["code"], str)
        self.assertIsInstance(body["error"]["message"], str)
        return headers

    def test_crud_and_false_patch(self):
        self.assertEqual(self.request("GET", "/todos")[2], [])
        row = self.create('한글 "quote" 😄')
        self.assertIs(row["completed"], False)
        uri = f'/todos/{row["id"]}'
        self.assertEqual(self.request("GET", uri)[2], row)
        changed = self.request("PATCH", uri, {"completed": True})
        self.assertEqual(changed[0], 200)
        self.assertIs(changed[2]["completed"], True)
        changed = self.request("PATCH", uri, {"title": "새 제목"})[2]
        self.assertIs(changed["completed"], True)
        changed = self.request("PATCH", uri, {"completed": False})[2]
        self.assertEqual(changed, dict(id=row["id"], title="새 제목", completed=False))
        self.assertEqual(self.request("DELETE", uri)[::2], (204, None))
        self.assert_error(404, "GET", uri)
        self.assert_error(404, "PATCH", uri, {"title": "없는 항목"})
        self.assert_error(404, "DELETE", uri)

    def test_pagination_and_order(self):
        rows = [self.create(str(i)) for i in range(4)]
        self.assertEqual(self.request("GET", "/todos?limit=2&offset=1")[2], rows[1:3])
        self.assertEqual(self.request("GET", "/todos?offset=999")[2], [])
        for query in ("limit=0", "limit=101", "offset=-1", "limit=a", "limit=", "limit=2&limit=3", "unexpected=1"):
            with self.subTest(query=query):
                self.assert_error(400, "GET", "/todos?" + query)

    def test_input_validation(self):
        for payload in ({}, {"title": ""}, {"title": " \t\n"}, {"title": "x" * 201},
                        {"title": None}, {"title": 3}, {"title": "a\x00b"},
                        {"title": "x", "completed": None}, {"title": "x", "completed": 0},
                        {"title": "x", "completed": "false"}, {"title": "x", "id": 1}, [], False):
            with self.subTest(payload=payload):
                self.assert_error(400, "POST", "/todos", payload)
        self.assertEqual(self.request("GET", "/todos")[2], [])
        row = self.create("x" * 200, completed=True)
        uri = f'/todos/{row["id"]}'
        for payload in ({}, {"title": "bad", "completed": None}, {"completed": 1}, {"foo": "x"}):
            self.assert_error(400, "PATCH", uri, payload)
            self.assertEqual(self.request("GET", uri)[2], row)

    def test_json_and_media_type(self):
        for raw in (b"", b"{", b"null", b'{"title":"x"} {}', b'{"title":"\xff"}', b'{"title":"x",}'):
            with self.subTest(raw=raw):
                self.assert_error(400, "POST", "/todos", raw=raw)
        self.assert_error(415, "POST", "/todos", raw=b'{}', content_type="text/plain")
        self.assert_error(415, "POST", "/todos")
        self.assert_error(413, "POST", "/todos", raw=b"x" * 65537)
        self.assert_error(413, "POST", "/todos", raw=b"x" * 65537, chunked=True)
        self.assertEqual(self.request("POST", "/todos", {"title": "chunked"}, chunked=True)[0], 201)
        self.assertEqual(self.request("POST", "/todos", {"title": "utf8"}, content_type="application/json; charset=utf-8")[0], 201)

    def test_route_and_method_errors(self):
        self.assert_error(404, "GET", "/missing")
        self.assert_error(404, "GET", "/todos/1/extra")
        for path in ("/todos/abc", "/todos/0", "/todos/-1", "/todos/9223372036854775808"):
            self.assert_error(400, "GET", path)
        headers = self.assert_error(405, "PUT", "/todos/1", {"title": "x"})
        self.assertIn("PATCH", headers["Allow"])
        self.assert_error(405, "DELETE", "/todos")
        self.assertEqual(self.request("HEAD", "/todos")[::2], (200, None))

    def test_sql_binding(self):
        title = "'); DROP TABLE todos; --"
        row = self.create(title)
        self.assertEqual(self.request("GET", f'/todos/{row["id"]}')[2]["title"], title)
        self.create("still works")

    def test_concurrent_creates_and_partial_updates(self):
        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(lambda i: self.request("POST", "/todos", {"title": str(i)}), range(16)))
        self.assertTrue(all(result[0] == 201 for result in results), results)
        self.assertEqual(len({result[2]["id"] for result in results}), 16)
        row = results[0][2]
        uri = f'/todos/{row["id"]}'
        with ThreadPoolExecutor(max_workers=2) as pool:
            updates = list(pool.map(lambda body: self.request("PATCH", uri, body),
                                    [{"title": "parallel"}, {"completed": True}]))
        self.assertTrue(all(result[0] == 200 for result in updates), updates)
        self.assertEqual(self.request("GET", uri)[2], dict(id=row["id"], title="parallel", completed=True))

    def test_restart_persistence(self):
        kept = self.create("유지", completed=True)
        removed = self.create("삭제")
        self.request("DELETE", f'/todos/{removed["id"]}')
        self.stop_server()
        self.start_server()
        self.assertEqual(self.request("GET", f'/todos/{kept["id"]}')[2], kept)
        self.assert_error(404, "GET", f'/todos/{removed["id"]}')


if __name__ == "__main__":
    unittest.main(verbosity=2)
