(require :asdf)
(let ((root (uiop:pathname-parent-directory-pathname
             (uiop:pathname-directory-pathname *load-truename*))))
  (asdf:load-asd (merge-pathnames "clisp-todo-api.asd" root)))
(asdf:load-system "clisp-todo-api")
