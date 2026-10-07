# macOS 개발환경

## 구성

- SBCL: Common Lisp 컴파일러·REPL
- Qlot 1.8.4: 프로젝트 안의 `.tools/qlot`에 설치하는 의존성 도구
- ASDF: `common-lisp-todo-lab.asd`에 소스와 의존성 선언
- SQLite: 로컬 파일 기반 영속 저장소
- Neovim: lazy.nvim + Vlime + Paredit

## 설치와 실행

```sh
brew install sbcl openssl@3 sqlite
cd /Users/yoophi/project/common-lisp-todo-lab
make setup
make test
make dev
```

다른 터미널에서 상태 확인:

```sh
curl http://127.0.0.1:8080/health
```

`make setup`은 체크섬을 검증한 Qlot을 프로젝트에 설치하고 `qlfile.lock`에 고정된 의존성을 받는다. `.tools/`와 `.qlot/`은 Git에서 제외한다.

macOS에서 OpenSSL 4를 사용하는 경우 현재 의존성의 `ASN1_STRING_data` 오류가 발생할 수 있다. 이 환경은 OpenSSL 3으로 검증한다. 이 머신에서는 OpenSSL 4의 링크를 해제하고 기존 OpenSSL 3 링크를 복구했다. 다른 프로젝트 때문에 OpenSSL 4가 필요한 머신에서는 전역 링크 변경 대신 CL+SSL의 라이브러리 경로를 별도 설정한다.

## REPL 개발

```sh
make repl
```

```lisp
(todo-api:start)
(todo-api:stop)
```

`HOST`와 `PORT` 환경변수로 수신 주소를 지정한다. 로컬 기본 주소는 `127.0.0.1:8080`이다.

`DATABASE_PATH`는 SQLite 파일 경로이며 기본값은 작업 디렉터리의 `data/todos.db`다. 서버 시작 시 디렉터리와 Todo 테이블을 준비한다. `/health`와 Todo CRUD를 제공하며 [API 문서](api.md)에 요청·응답 규약이 있다.

```sh
DATABASE_PATH=data/dev.db PORT=8081 make dev
make build
PORT=8081 ./build/todo-api
```

`make build`는 현재 OS·CPU용 실행 파일을 생성한다. macOS 결과물을 Linux 배포에 사용하지 않는다.

`make check`는 Lisp 테스트와 빌드 후 Python 3 표준 라이브러리로 실행 파일의 HTTP 응답, `DATABASE_PATH`, 재시작 영속화 및 SIGTERM 정상 종료를 검증한다. 테스트 데이터는 임시 디렉터리에서 생성·삭제한다.

## Docker 런타임 준비

이 머신에서는 프로젝트 이름 변경 전에 생성한 Colima 프로필 `clisp-todo-api`(CPU 2개, 메모리 4GiB, 디스크 20GiB)를 계속 사용한다. Docker 컨텍스트 이름도 `colima-clisp-todo-api`다.

```sh
colima start --profile clisp-todo-api
docker --context colima-clisp-todo-api info
docker-compose version
# 개발 종료 후 VM 중지
colima stop --profile clisp-todo-api
```

Compose는 Homebrew의 `docker-compose` 명령을 사용한다. 배포용 Dockerfile·Compose 파일 작성과 Linux 이미지 검증은 `td-71e5df`에서 진행한다.

## Neovim 설정

사용자의 기존 `~/.config/nvim`은 lazy.nvim 기반이다. 기존 플러그인을 유지하면서 다음 파일을 추가했다.

- `lua/plugins/lisp.lua`: Vlime와 Paredit을 Lisp 파일에서 로드
- `lua/config/lisp.lua`: 가까운 `qlfile`을 찾아 프로젝트의 `.qlot/setup.lisp`으로 SBCL 시작
- `after/ftplugin/lisp.lua`: 공백 2칸, Lisp 문법 강조, 주석과 들여쓰기 설정

`.lisp`, `.cl`, `.asd`를 Lisp 파일로 인식한다. 문법 강조는 Neovim 기본 기능을 사용하며, 연결 후 들여쓰기와 완성은 Vlime가 제공한다. 별도 Common Lisp LSP는 필요하지 않다. 실행 중인 Lisp 이미지에 연결하는 방식이다.

```sh
cd /Users/yoophi/project/common-lisp-todo-lab
nvim src/server.lisp
```

기존 Space leader를 유지하며 Vlime는 기본 localleader인 백슬래시(`\`)를 사용한다.

| 키 | 기능 |
| --- | --- |
| `\rr` | 프로젝트 의존성을 사용하는 SBCL/Vlime 시작 및 연결 |
| `\rs` | 시작한 서버 중지 |
| `\ss` | 커서 위치 표현식 평가 |
| `\st` | 최상위 표현식 평가 |
| `\si` | 평가할 코드를 입력하는 버퍼 열기 |
| 시각 선택 후 `\s` | 선택한 코드 평가 |
| `\of` | 현재 파일 컴파일 |
| `\xd` | 심볼 정의 찾기 |
| `\da` | 심볼 설명 |
| `\mm` | 매크로 확장 |
| 입력 모드 `Ctrl-x Ctrl-o` | Lisp 심볼 완성 |
| `\pW` | Paredit: 심볼을 괄호로 감싸기 |
| `\pS` | Paredit: 현재 리스트의 바깥 괄호 제거 |
| `gg=G` | 전체 버퍼 들여쓰기 |

Vlime 연결 후 `\si` 입력 버퍼에서 프로젝트를 로드하고 서버를 시작한다. 코드 입력 후 일반 모드의 Enter로 평가한다.

```lisp
(load "scripts/load.lisp")
(todo-api:start)
```

첫 연결 시 Swank 등을 컴파일하므로 시간이 걸릴 수 있다. `\rv`로 서버 출력을 확인한다. `:help vlime`와 `:help paredit`에서 상세 기능을 볼 수 있다.

참고: [Vlime](https://github.com/vlime/vlime), [Paredit](https://github.com/kovisoft/paredit), [Qlot](https://github.com/fukamachi/qlot)
