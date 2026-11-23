---
name: analysis-writing
description: Rules the re-analysis team (data-analyst, ml-engineer) follows when designing analyses and writing results as text or code output. Uses the textbook-based analysis plan (reviews/교재기반_분석안_조율_2026-11-23.md) as the methodological baseline. Use when choosing analysis methods, and when writing or editing markdown/result cells in src/재검증/ notebooks, reviews/재분석_*.md reports, presentation conclusion sentences, or chart titles/captions.
---

# Analysis writing rules

Shared rules (no overstated causality, no investment advice, number sourcing, etc.) come from `AGENTS.md`. This file adds only the analysis baseline and writing style not covered there.

**All outputs (notebook markdown, reports, chart text) are written in Korean.** Korean phrases quoted below are templates to use as-is.

## 0. Baseline: textbook-based analysis plan
Methods follow `reviews/교재기반_분석안_조율_2026-11-23.md` (based on chapters 1–11 of the course textbook 「오렌지3 with 파이썬」). Read it before designing any analysis.
- Per-question methods: follow section 2 (01~07 최종안) — textbook technique, design, cautions.
- Techniques not used or restricted: follow the table in section 3 (no random 7:3 split as the main result; no IQR deletion, SMOTE, or CNN, etc.).
- Apply section 1's shared agreements (group/time-ordered splits, outlier flags, leakage prevention, `SEED=42`) in every notebook.
- In the method description at the top of each notebook, state **which textbook chapter was used** and **what was changed from the textbook and why**.
- **Do not use analyses or techniques that are not in the plan.** Use one only when it is truly necessary to answer the research question, and then explain why in the notebook and report.
- If there is a reason to deviate from the plan, stop and ask the user before changing.

## 1. Four claim levels
Before writing a result sentence, decide its level and write no stronger than that level.

| Level | Evidence | Allowed wording (Korean) |
| --- | --- | --- |
| Simple change | Descriptive stats by period/region | "~에서 ~로 변했다", "~가 더 높았다" |
| Statistical association | Correlation, regression coefficients, tests | "~와 함께 움직였다", "~가 높을수록 가격이 높은 경향" |
| Predictive contribution | Model performance, feature importance | "~를 넣으면 예측 오차가 ~ 줄었다" |
| Assumption-based scenario | Calculation under assumptions | "~라고 가정하면 ~로 계산된다" |

- If a sentence mixes levels, write it at the lowest one.
- Never describe feature importance or regression coefficients as "영향" or "효과".
- Policy before/after comparisons are simple change. If pre-trends or overlapping events were controlled, state how.

## 2. Numbers
- **Default price unit is 만원 per ㎡.** Total price is secondary only; when used, the unit is 억원.
- Use % for rates of change and %p for differences between rates.
- Always report with each number:
  - **Sample size and period**, e.g. `n=12,345건, 2019-01~2024-12, 서울 25개 구`
  - **Uncertainty**: confidence interval, standard error, or p-value as applicable. With clustered SEs, state the cluster unit.
- If a region/period has a small, unstable sample, say so in the same sentence.

## 3. Notebook result cells
Result cells show only the values the analysis needs. Do not decorate output.
- Don't: separator/banner prints (`print("=" * 50)`), emoji, decorative text ("✅ 완료!", "분석 결과입니다"), `DataFrame.style` coloring/highlighting, printing the same value in multiple formats.
- Do: display needed tables as plain `DataFrame`; trim long tables to the needed rows/columns; explain what values mean in the markdown cell right below, not in printed output.
- No progress logs. Keep sanity-check output (counts, missing values) only if it informs a decision.

## 4. Notebook markdown
- Top: question, method and metrics, reason for choosing the method.
- Bottom: conclusion, limitations.
- Each conclusion sentence should make clear which cell or `outputs/재검증/` file supports it.

## 5. Re-analysis report (`reviews/재분석_*.md`)
For each question, in this order:
1. Method
2. Key results (apply section 2)
3. Confidence: one of 강함·보통·약함, plus a one-line justification
4. Limitations
5. Candidate presentation sentences: one or two sentences not exceeding the section 1 level

## 6. Chart titles and captions
- Titles state only what is shown. No conclusions or interpretation in titles.
  - e.g. "구별 ㎡당 중위가격 변화율 (2019-01~2024-12)"
- Put units in axis labels. Put sample size and source file in the caption.

## 7. Output files for a future dashboard
HTML conversion is **not** done now, but every `outputs/재검증/<번호>/` folder must be ready to drop into a single-page dashboard later (`web-builder` will read these files).
- **`summary.csv` per folder (required):** one row per headline number. Columns: `key, label, value, unit, sample_n, period, split_type, claim_level, source_file, note`.
  - `claim_level` ∈ `단순 변화 / 통계적 연관 / 예측 기여도 / 가정 시나리오` (section 1).
  - `split_type` ∈ `없음 / 무작위 / 그룹(단지) / 그룹(동) / 공간블록 / 시간순 / 워크포워드`.
- **One tidy CSV per chart:** long format, fixed snake_case English column names, UTF-8 (with BOM if Excel must open it), dates as `YYYY-MM` or `YYYY-Qn`. Name it after the chart, e.g. `fig_monthly_price.csv`.
  - Keep each chart CSV small (a few thousand rows at most). Sample scatter plots with `SEED=42` and say so in `note`.
  - Store summary values (quantiles for box plots, binned counts for histograms) instead of raw rows.
- **`meta.json` per folder:** question, method, textbook chapters used, sample period, sample size, data files used, limitations (Korean text). The dashboard shows these as-is.
- **Model performance:** save random-split and group/time-ordered results in the same table (`split_type` column). For cross-validation save mean and std.
- **Scenarios (07-2):** save a precomputed grid (`rate_delta, commute_delta, ..., value, value_low, value_high`). The dashboard must not recompute models.
- **Maps:** save `dong, gu, lat, lon, <value>` points. Do not depend on map tiles.
- **PNG:** only for charts hard to redraw in JS (e.g. tree diagrams). Width ≤ 1200px, about 200KB or less, Korean font, same title rules as section 6.
- Undervalued-동 rankings stay out of `summary.csv` and are marked `internal_only` in the filename.
