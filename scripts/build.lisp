(load (merge-pathnames "load.lisp" *load-truename*))
(sb-ext:save-lisp-and-die "build/todo-api" :toplevel #'todo-api:main :executable t)
