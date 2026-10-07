# macOS 개발환경

```sh
brew install sbcl openssl@3 sqlite
make setup
make repl
```

Qlot 1.8.4는 `.tools/qlot`에 설치하고 의존성을 `.qlot`에 보관한다. `qlfile.lock`은 배포 시에도 같은 Lisp 라이브러리를 사용하기 위해 커밋한다. `clisp-todo-api.asd`는 소스 로드 순서와 의존성을 선언하고, `src/package.lisp`는 패키지를 정의한다.

REPL에서 `(in-package :todo-api)`로 패키지에 들어가 표현식을 평가할 수 있다. HTTP 서버 실행은 아래 안내를 따른다.

macOS의 OpenSSL 4는 현재 Lisp 의존성과 호환 문제가 있어 OpenSSL 3을 사용한다. 자세한 Neovim 설정과 실행 검증은 후속 단계에서 문서화한다.

## HTTP 서버와 실행 파일

`make dev`로 서버를 실행하고 `curl http://127.0.0.1:8080/health`로 JSON 응답을 확인한다. REPL에서는 `(todo-api:start)`와 `(todo-api:stop)`을 사용한다. HOST/PORT 환경변수를 지원하며 기본값은 127.0.0.1:8080이다.

`make build`는 현재 OS·CPU용 `build/todo-api`를 만든다. SIGINT/SIGTERM 요청 시 메인 루프를 종료하고 서버를 정리한다.
