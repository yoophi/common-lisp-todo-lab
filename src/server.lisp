(in-package #:todo-api)

(defvar *server* nil)

(defun make-app ()
  (let ((app (make-instance 'ningle:app)))
    (setf (ningle:route app "/health" :method :get)
          (lambda (params)
            (declare (ignore params))
            (let ((body (make-hash-table :test 'equal)))
              (setf (gethash "status" body) "ok")
              (list 200 '(:content-type "application/json; charset=utf-8")
                    (list (com.inuoe.jzon:stringify body))))))
    app))

(defun start (&key (host (or (uiop:getenv "HOST") "127.0.0.1"))
                   (port (parse-integer (or (uiop:getenv "PORT") "8080"))))
  (when *server* (error "Server is already running."))
  (initialize-database)
  (setf *server* (clack:clackup (make-app) :server :hunchentoot
                                        :address host :port port
                                        :use-thread t :debug nil)))

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
