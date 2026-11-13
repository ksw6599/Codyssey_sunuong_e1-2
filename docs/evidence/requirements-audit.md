# E1-2 최종 요구사항 검수

미션 지문 확인: 2026-11-13. 실제 구현과 실행 기록을 대조했습니다.

| 요구 | 구현과 실제 증거 |
|---|---|
| Python 3.10+, 표준 라이브러리 | environment.txt의 Python 3.12.3, 5개 실행 파일의 import |
| 메뉴 5개와 잘못된 입력 | game.py / inputs.py, verification.log |
| Quiz / QuizGame과 기능별 메서드 | quiz.py / game.py |
| 같은 주제의 기본 문제 5개 이상 | defaults.py에 4지선다 6개 |
| 추가·목록·정오답·최고 점수 | add_quiz.txt / list.txt / play.txt / score.txt |
| 프로젝트 루트 state.json, UTF-8 | STATE_FILE, 재시작 검증, state-after-demo.json |
| 공백·빈 입력·문자·범위 오류 | 정상 실행 시나리오와 InputTests |
| EOF와 Ctrl+C | 실제 EOF 2개 시나리오, 실제 SIGINT 시나리오 |
| 손상 파일·읽기/쓰기 실패 | 실제 손상·읽기/쓰기 오류 + 모의 교체/백업 실패 테스트 |
| 새 공개 저장소와 10개 이상 커밋 | Codyssey_sunuong_e1-2, git-graph.txt에 17개 커밋 시점 기록 |
| branch / checkout / merge | feature/quiz-play, 실제 2-parent merge 12c35a2 |
| init/add/commit/push/clone/pull | 최초 2935a42 및 git-workflow.log / clone-pull.log |
| clone에서 수정·push, 원래 폴더 pull | 9e151b1을 두 폴더에서 확인한 clone-pull.log |
| README 필수 6개 항목 | 개요·주제·실행·기능·구조·데이터 스키마 |
| 환경·프로그램·그래프 캡처 | docs/screenshots/의 실제 출력 기록 뷰어 캡처 7개 |

검증 결과는 **정상 진입점 12개 시나리오 + 단위 테스트 19개 통과**입니다. 캡처는 실제 명령과 프로그램의 표준출력을 열어 저장한 이미지이며 원본 텍스트 기록과 연결됩니다. 네이티브 VS Code 터미널을 직접 캡처한 이미지라고 주장하지 않습니다.

선택 보너스는 구현하지 않았습니다. 여러 프로세스의 동시 쓰기 충돌 해결은 범위 밖입니다. 저장 실패는 안내하며 성공으로 처리하지 않습니다. 플랫폼의 평가 요청 버튼은 누르지 않았습니다.
