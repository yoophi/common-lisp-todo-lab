QLOT := .tools/qlot/bin/qlot
LISP := $(QLOT) exec sbcl --noinform

.PHONY: setup repl
setup:
	sh scripts/bootstrap.sh
repl:
	$(LISP) --load scripts/load.lisp

.PHONY: dev build
dev:
	$(LISP) --load scripts/load.lisp --eval '(todo-api:main)'
build:
	mkdir -p build
	$(LISP) --script scripts/build.lisp

.PHONY: test
test:
	$(LISP) --script tests/smoke.lisp
