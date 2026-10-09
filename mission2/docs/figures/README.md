# 미션 2 구조도

실제 코드와 제공된 캡처를 바탕으로 작성한 설명용 그림이다. 실행 화면이나 실측 결과를 대체하지 않는다.

| 그림 | PNG | SVG | 편집 원본 |
| --- | --- | --- | --- |
| PC–Pi–OpenCR 연결 | [PNG](system-connection.png) | [SVG](system-connection.svg) | [DOT](system-connection.dot) |
| 주행·팔·그리퍼 명령 경로 | [PNG](control-flow.png) | [SVG](control-flow.svg) | [DOT](control-flow.dot) |
| 네 터미널 역할 | [PNG](terminal-layout.png) | [SVG](terminal-layout.svg) | [DOT](terminal-layout.dot) |

PNG는 바로 삽입하는 이미지, SVG는 확대용 벡터, DOT는 Graphviz 편집 원본이다. 전체 구조와 제어 흐름의 설명은 [시스템 구조](../architecture.md)에 있다.

Graphviz와 Noto Sans CJK KR 글꼴이 있는 환경에서 이 폴더로 이동하여 재생성한다.

```bash
for name in system-connection control-flow terminal-layout; do
  dot -Tpng -Gdpi=140 "$name.dot" -o "$name.png"
  dot -Tsvg -Gdpi=140 "$name.dot" -o "$name.svg"
done
```
