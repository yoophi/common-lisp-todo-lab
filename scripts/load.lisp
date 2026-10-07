(require :asdf)
(let ((root (uiop:pathname-parent-directory-pathname
             (uiop:pathname-directory-pathname *load-truename*))))
  (asdf:load-asd (merge-pathnames "common-lisp-todo-lab.asd" root)))
(asdf:load-system "common-lisp-todo-lab")
