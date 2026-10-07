# Common Lisp와 SBCL

Common Lisp은 언어이며 SBCL(Steel Bank Common Lisp)은 그 언어를 컴파일하고 실행하는 구현체다. Python과 CPython의 관계에 비유할 수 있다. 함수, 매크로, CLOS 등은 언어의 기능이고, 컴파일러·GC·디버거의 구체적인 구현은 SBCL이 제공한다.

## 역사

SBCL은 1999년 12월 카네기 멜런 대학교에서 유래한 CMUCL에서 분리됐다. 컴파일러와 런타임을 계승하면서 유지보수성과 부트스트래핑, 즉 소스로부터 시스템 자체를 다시 만드는 과정을 개선하는 데 중점을 뒀다.

Steel과 Bank라는 이름은 Andrew Carnegie의 철강업과 Andrew Mellon의 금융업에서 따왔다. [공식 역사](https://www.sbcl.org/history.html)

## 다른 구현체와의 비교

| 구현체 | 특징 | SBCL을 선택하는 이유 |
| --- | --- | --- |
| CLISP | 인터프리터와 바이트코드 컴파일러 기반 | 네이티브 기계어 컴파일과 최적화 활용 |
| ABCL | JVM에서 실행하며 Java와 연동 | JVM 없이 독립적인 네이티브 서버 구성 |
| LispWorks | 컴파일러, 통합 IDE, CAPI GUI 도구를 제공하는 상용 제품 | 외부 편집기와 오픈소스 도구로 개발·배포 환경 구성 |

각 구현체의 지향점은 다르다. 이 비교는 SBCL이 모든 작업에서 가장 빠르다는 의미가 아니다.

참고: [CLISP](https://clisp.sourceforge.io/), [ABCL](https://abcl.org/), [LispWorks](https://www.lispworks.com/products/lispworks.html)

## SBCL의 장점

- **최적화와 타입 추론:** 컴파일러가 타입을 추론하고 타입 선언을 활용해 효율적인 코드를 생성한다. 최적화하지 못한 이유도 알려준다.
- **컴파일 시 진단:** 타입 불일치와 잘못된 함수 호출 등을 실행 전에 발견하는 데 도움을 준다. 모든 오류를 정적으로 발견하는 것은 아니다.
- **분석 도구:** 프로파일러, 디스어셈블러, 메모리 관련 도구로 병목을 조사할 수 있다.
- **네이티브 스레드와 실행 파일 생성:** 서버 병렬 처리와 배포에 활용할 수 있다. SBCL만의 독점 기능은 아니다.
- **라이선스:** 대부분 퍼블릭 도메인이며 일부는 BSD 계열이다. 사용하는 외부 라이브러리의 라이선스는 별도로 적용된다.

참고: [SBCL 설명서](https://www.sbcl.org/manual/), [라이선스 안내](https://www.sbcl.org/history.html)

## 고려할 점

최적화 컴파일에는 시간이 들 수 있고, 통합 GUI 개발 환경은 별도로 구성해야 한다. 컴파일된 파일은 SBCL 버전·OS·CPU에 종속되므로 배포 대상 환경에서 다시 빌드한다.

이 프로젝트는 SBCL의 진단 기능을 활용해 macOS에서 개발하고, Linux Docker 환경에서 실행 파일을 만든다. SQLite 같은 외부 공유 라이브러리는 실행 이미지에도 포함해야 한다.
