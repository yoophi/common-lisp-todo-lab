# Todo RESTful API

[swagger.json](../swagger.json)은 OpenAPI 3.0.3 형식의 정적 명세다. Swagger Editor/UI에 가져와 사용할 수 있다. 현재 서버에 `/swagger.json` 또는 Swagger UI 경로를 제공하는 것은 아니다. 서버 주소는 IPv4 `http://127.0.0.1:8080`으로 지정했다.

명세 검증: `uvx --from openapi-spec-validator openapi-spec-validator swagger.json`

`make dev`로 시작한다. 기본값은 `HOST=127.0.0.1`, `PORT=8080`, `DATABASE_PATH=data/todos.db`다. SQLite 파일과 테이블은 시작 시 준비한다. 현재 API는 인증 없는 단일 Todo 목록을 제공한다.

## 데이터

```json
{"id":1,"title":"Common Lisp 공부","completed":false}
```

- `id`: 서버가 생성하는 양의 정수. 요청 본문에 지정하거나 수정할 수 없다.
- `title`: 공백만으로 이루어지지 않은 1~200자 문자열. 앞뒤 공백을 자동 제거하지 않으며 NUL 문자는 허용하지 않는다.
- `completed`: JSON 불리언. 생성 시 생략하면 `false`다. `null`, 숫자, 문자열은 허용하지 않는다.

## 엔드포인트

| 메서드 | 경로 | 성공 응답 |
| --- | --- | --- |
| GET | `/health` | 200, `{"status":"ok"}` |
| POST | `/todos` | 201, 생성된 Todo와 `Location` 헤더 |
| GET | `/todos` | 200, Todo 배열 (`[]` 가능) |
| GET | `/todos/:id` | 200, Todo |
| PATCH | `/todos/:id` | 200, 수정된 Todo |
| DELETE | `/todos/:id` | 204, 본문 없음 |

조회 경로에는 HEAD도 지원한다. 그 밖의 메서드는 405와 `Allow` 헤더를 반환한다. 경로는 후행 슬래시 없이 사용한다.

## 사용 예제

```sh
# 생성: 응답의 id와 Location을 확인한다.
curl -i http://127.0.0.1:8080/todos \
  -H 'Content-Type: application/json' \
  -d '{"title":"Common Lisp 공부"}'

# 목록과 단건 조회 (이하 1은 실제 응답의 id로 바꾼다.)
curl 'http://127.0.0.1:8080/todos?limit=20&offset=0'
curl http://127.0.0.1:8080/todos/1

# 완료 상태 변경
curl -X PATCH http://127.0.0.1:8080/todos/1 \
  -H 'Content-Type: application/json' \
  -d '{"completed":true}'

# 제목 수정과 완료 해제
curl -X PATCH http://127.0.0.1:8080/todos/1 \
  -H 'Content-Type: application/json' \
  -d '{"title":"SQLite 공부","completed":false}'

# 삭제
curl -i -X DELETE http://127.0.0.1:8080/todos/1
```

생성 시 `title`은 필수다. PATCH에는 `title`, `completed` 중 하나 이상을 전달한다. 생략한 필드는 유지하며 `completed: false`는 완료 상태를 해제한다. 두 필드 외의 필드는 거부한다. 잘못된 필드가 하나라도 있으면 전체 요청을 거부하고 데이터를 변경하지 않는다. PUT은 지원하지 않는다.

목록은 `id` 오름차순이다. `limit` 기본값은 50, 허용 범위는 1~100이다. `offset` 기본값은 0이며 0 이상의 SQLite 정수 범위 값을 받는다. 범위 밖 또는 잘못된 정수, 중복·알 수 없는 쿼리 매개변수는 400을 반환한다. 동시 삽입·삭제 중 페이지 간 일관된 스냅샷을 보장하지는 않는다.

조회·수정·삭제 대상이 없으면 404다. 이미 삭제된 Todo를 다시 삭제해도 404다.

## 오류

애플리케이션 오류는 JSON으로 반환한다.

```json
{"error":{"code":"not_found","message":"Todo not found."}}
```

| 상태 | 상황 |
| --- | --- |
| 400 | 잘못된 JSON·UTF-8, 필드 타입·값, ID, 쿼리 매개변수 |
| 404 | 존재하지 않는 Todo 또는 경로 |
| 405 | 지원하지 않는 HTTP 메서드 (`Allow` 헤더 포함) |
| 413 | 요청 본문이 64 KiB 초과 |
| 415 | POST/PATCH의 Content-Type이 application/json이 아님 |
| 500 | 내부 처리 오류. 세부 사항은 서버 로그에 기록 |

POST/PATCH 본문은 UTF-8 JSON 객체여야 한다. 최대 JSON 중첩 깊이는 16이다. HTTP 전송 자체가 잘못된 요청은 웹서버 단계에서 거부될 수 있다.

## 영속화와 동시성

SQLite WAL 모드를 사용한다. DB 연결을 작업마다 열고 닫으며 잠금 대기 시간은 5초다. SQL 값은 매개변수로 바인딩한다. 생성·수정과 결과 조회를 같은 트랜잭션에서 실행한다. PATCH는 단일 UPDATE에서 전달한 필드만 바꾸므로 서로 다른 필드의 동시 수정이 누락되지 않는다. 동일 필드의 동시 수정은 마지막 쓰기 값이 남는다.

같은 `DATABASE_PATH`로 재시작하면 데이터가 유지된다. WAL 모드의 데이터 보존을 위해 DB 파일이 있는 디렉터리를 함께 관리한다. Docker 데이터 볼륨 구성은 배포 태스크에서 진행한다.

## 검증

```sh
make check
# 실행 파일이 이미 최신이면 HTTP 테스트만 실행
python3 tests/crud_http.py
```

임시 DB와 빈 작업 디렉터리에서 실행 파일을 기동한다. CRUD·부분 수정, 페이지 조회, 입력 검증, JSON과 본문 제한, 경로·메서드 오류, SQL 바인딩, 동시 작업, 재시작 영속화를 검증하고 프로세스와 임시 데이터를 정리한다.
