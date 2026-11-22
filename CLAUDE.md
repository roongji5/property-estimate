@AGENTS.md

# Claude Code-specific guide

Follow the shared rules in AGENTS.md above. This file covers only what applies to Claude Code.

## Subagents (`.claude/agents/`)
| Name | Role | Output |
| --- | --- | --- |
| `review-stats` | Statistical·econometric review (ADF, Granger, panel, models) | `reviews/review-stats_<date>.md` |
| `review-data` | Data quality (counts, periods, missing values, joins) | `reviews/review-data_<date>.md` |
| `review-domain` | Real-estate domain interpretation, overstated-causality check | `reviews/review-domain_<date>.md` |
| `review-repro` | Re-runs notebooks on copies and compares results | `reviews/review-repro_<date>.md` |
| `web-builder` | Collects `outputs/` into a single `web/index.html` file | `web/index.html`, `web/build.py` |
| `data-analyst` | New analysis of questions 01–06 (EDA, statistics, charts), designed from raw data | `src/재검증/00~06`, `outputs/재검증/`, `reviews/재분석_data-analyst_<date>.md` |
| `ml-engineer` | New analysis of question 07 and predictive modeling for 03–05 | `src/재검증/07*`, `outputs/재검증/07/`, `reviews/재분석_ml-engineer_<date>.md` |

The re-analysis team answers the same research questions independently: it does not read the original notebooks or `outputs/`, and uses the review reports only as a list of pitfalls. It runs in order: `data-analyst` first (it writes the cleaned data to `outputs/재검증/00_정제/`), then `ml-engineer`. Original notebooks `src/01~07` stay untouched.

How to call them: "review-stats, review-data, review-domain, review-repro 에이전트로 분석 결과 점검해 줘", "web-builder로 웹 화면 만들어 줘"

- The review team **only reports findings**. Fixes happen after the user reads the reports and decides on a direction.
- `web-builder` writes only inside `web/`.

## Recommended workflow
1. Run the four reviewers → write reports to `reviews/`
2. User reviews the findings and decides how to fix them → apply fixes
3. Clean up the README (directly in the main session)
4. Generate the results page with `web-builder`

## Skills
- Put project skills in `.claude/skills/<name>/SKILL.md`.
- To connect one to `web-builder`, add its name to the `skills:` line in the frontmatter of `.claude/agents/web-builder.md`.
