QLOT := .tools/qlot/bin/qlot
LISP := $(QLOT) exec sbcl --noinform

.PHONY: setup repl
setup:
	sh scripts/bootstrap.sh
repl:
	$(LISP) --load scripts/load.lisp
