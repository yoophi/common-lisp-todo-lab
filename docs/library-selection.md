# Todo API 라이브러리 선택

## 목적과 상태

Common Lisp + SBCL로 Todo RESTful API 웹서비스를 구현하고 SQLite에 데이터를 영속화한다. macOS에서 개발하며 Linux Docker 환경에서 빌드·배포한다.

선택 기준은 작은 CRUD API를 이해하기 쉽게 구현하고 개발·배포 환경을 관리하기 쉬운가이다. 아래 조합을 사용하며 설치와 통합 검증은 후속 단계에서 진행한다.

| 역할 | 선택한 라이브러리 |
| --- | --- |
| HTTP 웹서버 | Hunchentoot |
| 웹 애플리케이션과 서버 연결 | Clack |
| HTTP 메서드·경로 라우팅 | Ningle |
| SQLite 접근 | CL-DBI + dbd-sqlite3 |
| JSON 생성·파싱 | Jzon (`com.inuoe.jzon`) |

## 웹서버와 라우팅

### 검토한 라이브러리

| 라이브러리 | 특징 | 판단 |
| --- | --- | --- |
| Hunchentoot | HTTP 서버, 요청·응답 처리, 로깅, 세션, 서버 시작·종료 기능 제공 | 기본 웹서비스 운영 기능을 갖추고 있어 선택 |
| Woo | libev 기반 비동기·논블로킹 HTTP 서버 | 동시 연결 처리 성능이 중요해질 때 검토할 대안 |

Hunchentoot는 진행 중인 요청 처리가 끝날 때까지 기다리는 종료 기능을 제공한다. 작은 Todo CRUD API에서는 서버의 시작·종료와 요청 처리를 명확하게 제어할 수 있는 구성이 적절하다고 판단했다.

Woo는 성능을 지향하지만 libev라는 네이티브 의존성이 추가된다. 이번 프로젝트에서 두 서버의 성능을 비교 측정한 것은 아니다.

### Ningle과 Clack의 역할

Ningle과 Clack은 Hunchentoot와 경쟁하는 서버가 아니라 함께 사용하는 구성 요소다.

| 구성 요소 | 담당 역할 |
| --- | --- |
| Hunchentoot | 실제 HTTP 연결 수신과 응답 전송 |
| Clack | 웹 애플리케이션과 HTTP 서버 사이의 공통 인터페이스 |
| Ningle | `GET /todos`, `PATCH /todos/:id` 등 메서드와 경로 라우팅 |

Hunchentoot만으로도 API를 구현할 수 있다. 다만 HTTP 메서드와 경로 매개변수를 간결하게 다루기 위해 Ningle + Clack을 함께 사용한다. 그 대신 학습할 계층과 의존성은 늘어난다.

참고: [Hunchentoot 공식 문서](https://edicl.github.io/hunchentoot/), [Woo 저장소](https://github.com/fukamachi/woo), [Clack 저장소](https://github.com/fukamachi/clack), [Ningle 저장소](https://github.com/fukamachi/ningle)

## SQLite 접근

### 검토한 라이브러리

| 라이브러리 | 특징 | 판단 |
| --- | --- | --- |
| CL-DBI + dbd-sqlite3 | 공통 DB 인터페이스와 SQLite 드라이버. SQL 매개변수 바인딩, 결과 조회, 트랜잭션 제공 | 일관된 연결·쿼리·트랜잭션 API를 사용할 수 있어 선택 |
| cl-sqlite | SQLite에 직접 접근하는 Common Lisp 바인딩 | SQLite 전용으로 얇게 구성하고 싶을 때 대안 |

CL-DBI를 사용해도 SQL은 직접 작성한다. ORM처럼 객체와 테이블을 자동으로 매핑하는 방식은 아니다. Todo CRUD에는 SQL을 명시적으로 작성하는 편이 동작을 파악하기 쉽다고 판단했다.

직접 바인딩보다 추상화 계층이 하나 추가된다. 여러 DB를 지원하지만 DB 변경 시 SQL과 스키마까지 자동으로 호환되는 것은 아니다.

### 구현 시 고려 사항

- SQL 값은 문자열 결합 대신 `prepare`와 `execute`의 매개변수 바인딩으로 전달한다.
- 여러 변경을 하나의 작업으로 처리할 때는 `with-transaction`을 사용한다.
- DB 연결 하나를 여러 요청이 무분별하게 공유하지 않도록 연결 수명을 관리한다.
- SQL 결과를 API 응답 객체로 변환하는 함수를 둔다.
- 실행 파일을 만들 때 SQLite 드라이버가 포함되도록 `dbd-sqlite3`를 ASDF 의존성에 명시한다.
- Docker 실행 이미지에 SQLite 공유 라이브러리를 포함하고, 데이터베이스 디렉터리는 영속 볼륨으로 유지한다.

참고: [CL-DBI 문서](https://github.com/fukamachi/cl-dbi), [cl-sqlite 저장소](https://github.com/TeMPOraL/cl-sqlite)

## JSON 생성과 파싱

### 검토한 라이브러리

| 라이브러리 | 특징 | 판단 |
| --- | --- | --- |
| Jzon | RFC 8259를 지향하는 JSON 파서·생성기. 객체·배열·불리언·null 매핑이 명확 | API 데이터 타입을 예측하기 쉬워 선택 |
| Jonathan | plist·alist 등 여러 Lisp 표현 지원, 인코더 생성 기능 제공, 성능 지향 | Lisp 리스트 기반 표현을 선호할 때 대안 |

Jzon은 요청 본문 파싱과 응답 JSON 생성에 함께 사용한다. 기본 타입 매핑은 다음과 같다.

| JSON | Common Lisp |
| --- | --- |
| `true` | `t` |
| `false` | `nil` |
| `null` | `'null` |
| 배열 | 벡터, 빈 배열은 `#()` |
| 객체 | `equal` 비교를 사용하는 해시 테이블 |

Todo API에서는 `completed: false`, 빈 목록 `[]`, 필드 생략을 구분해야 한다. `PATCH /todos/:id` 처리 시 `gethash`의 값과 존재 여부를 함께 확인하여 완료 상태를 false로 바꾸는 요청과 완료 상태를 수정하지 않는 요청을 구별한다.

응답 객체는 문자열 키의 해시 테이블로 명시적으로 구성한다. DB에서 읽은 완료 상태도 JSON 불리언으로 변환한다.

Jonathan은 plist·alist를 직접 다루기 편하지만 표현 방식과 키 이름 변환 규칙을 정해야 한다. 이번 프로젝트에서는 Jzon의 명시적인 타입 매핑을 우선했다. 두 라이브러리의 성능은 프로젝트에서 비교 측정하지 않았다.

참고: [Jzon 공식 저장소](https://github.com/Zulu-Inuoe/jzon), [검토한 Jonathan 저장소](https://github.com/fukamachi/jonathan)
