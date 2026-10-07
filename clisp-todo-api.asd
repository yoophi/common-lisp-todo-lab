(asdf:defsystem "clisp-todo-api"
  :description "SQLite-backed Todo RESTful API"
  :version "0.1.0"
  :depends-on ("ningle" "clack" "clack-handler-hunchentoot" "hunchentoot" "com.inuoe.jzon")
  :serial t
  :components ((:file "src/package") (:file "src/server")))
