(asdf:defsystem "clisp-todo-api"
  :description "SQLite-backed Todo RESTful API"
  :version "0.1.0"
  :depends-on ("ningle" "clack" "clack-handler-hunchentoot"
               "hunchentoot" "dbi" "dbd-sqlite3" "com.inuoe.jzon" "babel")
  :serial t
  :components ((:file "src/package") (:file "src/database")
               (:file "src/api") (:file "src/server")))
