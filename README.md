# common-lisp-todo-lab

Common Lisp + SBCL로 Todo RESTful API를 구현하며 Lisp 개발을 배우는 학습용 프로젝트입니다. Todo 데이터는 SQLite에 영속화하며, 서비스가 재시작되어도 유지됩니다.

## 기술 선택

- **언어: Common Lisp**
- **실행 환경 및 컴파일러: SBCL (Steel Bank Common Lisp)**
- **영속 저장소: SQLite**
- **개발 환경: macOS**
- **빌드 및 배포 환경: Linux Docker**

Common Lisp은 언어이며, SBCL은 Common Lisp 구현체입니다. 이 프로젝트는 SBCL을 기준으로 개발하고 실행합니다.

프로젝트의 목표는 Todo 생성·조회·수정·삭제와 완료 상태 변경을 HTTP API로 제공하는 웹서비스를 만드는 것입니다.

## 제공 API

| 메서드 | 경로 | 기능 |
| --- | --- | --- |
| `POST` | `/todos` | Todo 생성 |
| `GET` | `/todos` | Todo 목록 조회 |
| `GET` | `/todos/:id` | Todo 단건 조회 |
| `PATCH` | `/todos/:id` | 제목 및 완료 상태 수정 |
| `DELETE` | `/todos/:id` | Todo 삭제 |

요청과 응답은 JSON을 사용합니다. 삭제 성공은 본문 없는 204 응답입니다. 목록에는 `limit`·`offset`을 지원하며, 상세 규약과 예제는 [API 문서](docs/api.md)를 참고하세요.

웹 계층은 Ningle + Clack + Hunchentoot, SQLite 접근은 CL-DBI + dbd-sqlite3, JSON 처리는 Jzon을 사용합니다. [선택 이유와 대안](docs/library-selection.md)을 참고하세요.

## 데이터 영속화 요구사항

- Todo 생성·조회·수정·삭제는 SQLite 데이터베이스를 기준으로 처리합니다.
- 서비스 프로세스를 종료하고 다시 시작해도 저장된 Todo와 완료 상태를 유지합니다.
- 데이터베이스 파일 경로는 `DATABASE_PATH` 환경변수로 설정합니다.
- Docker에서는 데이터베이스를 `/data/todos.db`에 저장하고, `/data`를 영속 볼륨으로 연결합니다.
- 컨테이너를 교체해도 같은 볼륨을 사용하면 기존 데이터를 유지해야 합니다.

## 개발 및 배포 계획

- macOS에서는 로컬 SBCL과 REPL을 사용해 개발합니다.
- 배포용 실행 파일은 대상 CPU 아키텍처에 맞는 Linux Docker 환경에서 빌드합니다.
- Docker Compose로 API 서비스와 SQLite 데이터 볼륨을 구성합니다.
- CRUD 동작과 서비스 재시작 후 데이터 유지 여부를 검증합니다.

## 현재 상태

macOS 개발환경과 Neovim Lisp 연동, SQLite 기반 Todo CRUD를 구현했습니다. 입력 검증, JSON 오류 응답, 페이지 조회, 동시 작업과 재시작 영속화를 HTTP 통합 테스트로 검증합니다. 배포용 Dockerfile·Compose 구성은 후속 태스크입니다.

## 빠른 시작

```sh
brew install sbcl openssl@3 sqlite
make setup
make test
make dev
```

다른 터미널에서 `curl http://127.0.0.1:8080/health`로 확인합니다. 서버 기본값은 `HOST=127.0.0.1`, `PORT=8080`, `DATABASE_PATH=data/todos.db`입니다.

- `make repl`: 프로젝트를 로드한 SBCL REPL
- `make build`: 현재 OS·CPU용 `build/todo-api` 실행 파일 생성
- `make check`: Lisp 테스트, 빌드, HTTP·영속화 통합 테스트
- [API 사용법과 응답 규약](docs/api.md)
- [OpenAPI 3.0.3 명세 (swagger.json)](swagger.json): Swagger Editor/UI에 가져올 수 있는 정적 명세
- [macOS 및 Neovim 개발 안내](docs/development.md)
- [SBCL 역사와 구현체 비교](docs/sbcl-overview.md)

## 개발 태스크

- `td-3af8e6`: macOS 개발 환경 구성
- `td-e76b40`: SQLite 기반 Todo RESTful API 구현 및 통합 테스트
- `td-71e5df`: Docker 빌드·배포 환경 구성

프로젝트 디렉터리에서 `td list`로 상태를 확인합니다.

## 참고 자료

- [SBCL 공식 사이트](https://www.sbcl.org/)
- [SBCL 사용자 설명서](https://www.sbcl.org/manual/)
- [Common Lisp HyperSpec](https://www.lispworks.com/documentation/HyperSpec/Front/index.htm)
