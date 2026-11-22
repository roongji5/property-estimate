@AGENTS.md

# Claude Code 전용 안내

공통 규칙은 위의 AGENTS.md를 따른다. 이 파일에는 Claude Code에만 해당하는 내용을 적는다.

## 서브 에이전트 (`.claude/agents/`)
| 이름 | 역할 | 결과물 |
| --- | --- | --- |
| `review-stats` | 통계·계량 검증 (ADF, 그레인저, 패널, 모형) | `reviews/review-stats_<날짜>.md` |
| `review-data` | 데이터 품질 (건수, 기간, 결측, 조인) | `reviews/review-data_<날짜>.md` |
| `review-domain` | 부동산 도메인 해석, 인과 과장 점검 | `reviews/review-domain_<날짜>.md` |
| `review-repro` | 노트북을 복사본으로 재실행해 결과 비교 | `reviews/review-repro_<날짜>.md` |
| `web-builder` | `outputs/`를 모아 `web/index.html` 파일 하나로 생성 | `web/index.html`, `web/build.py` |

부르는 법: "review-stats, review-data, review-domain, review-repro 에이전트로 분석 결과 점검해 줘", "web-builder로 웹 화면 만들어 줘"

- 점검팀은 **지적만** 한다. 수정은 사용자가 보고서를 보고 방향을 정한 뒤에 한다.
- `web-builder`는 `web/` 안에만 쓴다.

## 권장 작업 순서
1. 점검팀 4명 실행 → `reviews/` 보고서 작성
2. 사용자가 지적 사항을 검토하고 수정 방향 결정 → 수정
3. README 정리(메인 세션에서 직접)
4. `web-builder`로 결과 화면 생성

## 스킬
- 프로젝트 skill은 `.claude/skills/<이름>/SKILL.md`에 둔다.
- `web-builder`에 연결하려면 `.claude/agents/web-builder.md` frontmatter의 `skills:` 줄에 이름을 적는다.
