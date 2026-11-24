# AGENTS.md

Rules for any AI coding tool (Claude Code, Codex, etc.) working in this repository. There are no separate agent files; this file holds all rules.

## Task
- Follow `README.md`: its overview, research questions, and development roadmap define the work. If this file and `README.md` disagree on what to do, `README.md` wins.
- Analyze the research questions in `README.md` using the files in `data/`, and visualize the results.

## Working with the user
- Write notebooks **one cell at a time, together with the user.** After writing a cell, show it to the user and wait for their check before writing the next cell.

## Folders
| Folder | Contents | How to handle |
| --- | --- | --- |
| `data/` | Source data (transactions, education, commute, policy, interest rates) | **Read only** |
| `src/` | Analysis code files (notebooks). Put all new code files here | |
| `outputs/` | Results (CSV, PNG) made by the code in `src/`. Create this folder if it does not exist | |
| `src/05_직주근접_가격_분석.ipynb` | Earlier notebook kept for its Google Routes API call code | |

- **Treat `구버전/` as if it does not exist.** Do not read, reference, copy from, run, or modify anything in it.

## Rules
- **Do not overstate causality.** Distinguish simple change, statistical association, predictive performance, and assumption-based scenarios. Write "rose because of ~" only when the analysis method supports it.
- **Ask before installing packages** (`pip install`, etc.).
- **Never commit or push on your own.** Commit or push only when the user asks.

## Language
- Write all notebook Markdown, code comments, chart text (titles, axis labels, legends), and answers to the user in **Korean**.
- Use a Korean font in charts so the text is not broken.

## Code level
- Use only the techniques covered in the course textbook 「오렌지3 with 파이썬」 (summary: `reviews/교재기반_분석안_조율_2026-11-23.md`, "교재 기법 요약" table):
  | Chapter | Techniques |
  | --- | --- |
  | 1–2 | 7:3 train/test split, stratify, 10-fold cross-validation, train/validation/test split, 6-step workflow |
  | 3 | Decision tree, feature importance |
  | 4 | kNN, MinMax scaling |
  | 5 | Multiple linear regression, extrapolation to future inputs |
  | 6 | Logistic regression, naive Bayes, IQR outlier handling, SMOTE, confusion matrix |
  | 7–8 | k-means, silhouette and elbow methods, map visualization |
  | 9 | Association rules (FP-Growth) |
  | 10 | MLP, overfitting |
  | 11 | CNN embeddings |
- Write code at the level of a **data science undergraduate student**: code a student can read, explain line by line, and reproduce. Use `pandas`, `numpy`, `matplotlib`/`seaborn`, and `scikit-learn`. No hand-written estimators, no clever one-liners.
- If a research question cannot be answered with these techniques, stop and ask the user before using anything else.

## Code comments
- Start every code cell with a one-line `#` comment that says what the cell does.
