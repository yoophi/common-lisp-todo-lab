QLOT := .tools/qlot/bin/qlot
LISP := $(QLOT) exec sbcl --noinform

.PHONY: setup repl dev test build check
setup:
	sh scripts/bootstrap.sh
repl:
	$(LISP) --load scripts/load.lisp
dev:
	$(LISP) --load scripts/load.lisp --eval '(todo-api:main)'
test:
	$(LISP) --script tests/smoke.lisp
build:
	mkdir -p build
	$(LISP) --script scripts/build.lisp
check: test build
	python3 tests/service_smoke.py
	python3 tests/crud_http.py
