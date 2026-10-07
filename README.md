# clisp-todo-api

Common Lisp + SBCL로 Todo RESTful API를 만드는 학습용 프로젝트다. SQLite에 데이터를 영속화하며 macOS에서 개발하고 Linux Docker로 배포하는 것을 목표로 한다.

## 학습 순서

1. Common Lisp 언어와 SBCL 구현체의 관계 및 라이브러리 선택
2. ASDF 시스템, 패키지, Qlot 의존성 관리와 REPL
3. Ningle·Clack·Hunchentoot로 최소 HTTP 서버와 JSON 응답
4. SQLite 연결, SQL 바인딩, 트랜잭션과 자원 정리
5. Todo CRUD, 입력 검증과 Common Lisp condition 처리
6. 실행 파일과 HTTP·재시작 영속화 검증
7. OpenAPI 명세로 외부 계약 표현

## 설계

- [SBCL의 역사와 특징](docs/sbcl-overview.md)
- [라이브러리 선택과 대안](docs/library-selection.md)

ASDF·패키지·의존성 관리와 REPL을 구성했다. [개발환경](docs/development.md)을 따라 `make setup`, `make repl`로 시작한다.
