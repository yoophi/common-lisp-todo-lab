(in-package #:todo-api)

(defun database-path ()
  (pathname (or (uiop:getenv "DATABASE_PATH") "data/todos.db")))

(defun initialize-database (&optional (path (database-path)))
  (ensure-directories-exist path)
  (dbi:with-connection (connection :sqlite3 :database-name path :busy-timeout 5000)
    (dbi:do-sql connection "PRAGMA journal_mode=WAL")
    (dbi:do-sql connection
      "CREATE TABLE IF NOT EXISTS todos (
         id INTEGER PRIMARY KEY AUTOINCREMENT,
         title TEXT NOT NULL,
         completed INTEGER NOT NULL DEFAULT 0 CHECK (completed IN (0, 1))
       )"))
  path)

(defvar *database-path* nil "Bound per application, independent of later CWD changes.")

(defmacro with-database ((connection) &body body)
  `(dbi:with-connection (,connection :sqlite3 :database-name *database-path*
                                    :busy-timeout 5000)
     ,@body))

(defun query-rows (connection sql &optional parameters)
  (let ((query (dbi:prepare connection sql)))
    (unwind-protect (dbi:fetch-all (dbi:execute query parameters))
      (dbi:free-query-resources query))))

(defun find-todo (connection id)
  (first (query-rows connection "SELECT id, title, completed FROM todos WHERE id = ?"
                     (list id))))

(defun list-todos (limit offset)
  (with-database (connection)
    (query-rows connection
      "SELECT id, title, completed FROM todos ORDER BY id ASC LIMIT ? OFFSET ?"
      (list limit offset))))

(defun get-todo (id)
  (with-database (connection) (find-todo connection id)))

(defun create-todo (title completed)
  (with-database (connection)
    (dbi:with-transaction connection
      (dbi:do-sql connection "INSERT INTO todos (title, completed) VALUES (?, ?)"
                  (list title (if completed 1 0)))
      (first (query-rows connection
        "SELECT id, title, completed FROM todos WHERE id = last_insert_rowid()")))))

(defun update-todo (id title title-p completed completed-p)
  (with-database (connection)
    (dbi:with-transaction connection
      ;; A single UPDATE preserves omitted fields, even under concurrent PATCHes.
      (when (plusp (dbi:do-sql connection
                     "UPDATE todos SET title = CASE WHEN ? THEN ? ELSE title END,
                       completed = CASE WHEN ? THEN ? ELSE completed END WHERE id = ?"
                     (list (if title-p 1 0) title (if completed-p 1 0)
                           (if completed 1 0) id)))
        (find-todo connection id)))))

(defun delete-todo (id)
  (with-database (connection)
    (plusp (dbi:do-sql connection "DELETE FROM todos WHERE id = ?" (list id)))))
