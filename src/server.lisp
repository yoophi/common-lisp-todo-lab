(in-package #:todo-api)

(defvar *server* nil)

(defun make-app (path)
  (api-boundary (configure-routes (make-instance 'todo-app)) path))

(defun start (&key (host (or (uiop:getenv "HOST") "127.0.0.1"))
                   (port (parse-integer (or (uiop:getenv "PORT") "8080"))))
  (when *server* (error "Server is already running."))
  (let ((path (merge-pathnames (database-path) (uiop:getcwd))))
    (initialize-database path)
    (setf *server* (clack:clackup (make-app path) :server :hunchentoot
                                        :address host :port port
                                        :use-thread t :debug nil))))

(defun stop ()
  (when *server*
    (clack:stop *server*)
    (setf *server* nil)))

(defun main ()
  (let ((shutdown nil))
    (flet ((request-shutdown (&rest arguments)
             (declare (ignore arguments))
             (setf shutdown t)))
      (sb-sys:enable-interrupt sb-unix:sigterm #'request-shutdown)
      (sb-sys:enable-interrupt sb-unix:sigint #'request-shutdown)
      (start)
      (unwind-protect (loop until shutdown do (sleep 0.1)) (stop)))))
