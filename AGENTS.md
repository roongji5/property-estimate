# AGENTS.md

Shared guidelines for every AI coding tool (Codex, Claude Code, etc.) working in this repository.

## Project overview
- Analyzes Seoul apartment transaction prices (2017-10 to 2026-10) and how they relate to apartment characteristics, education environment, job-housing proximity, policy, and interest rates.
- Analysis is done in Python + Jupyter Notebook (`src/01~07`).
- Results will be shown as a local HTML·CSS·JavaScript page with no database (`web/`).
- See `README.md` for details.

## Folder structure
| Folder | Contents | How to handle |
| --- | --- | --- |
| `data/` | Consolidated transaction Excel file, education·commute·policy source data, `원본폴더` | **Read only** |
| `src/` | Analysis notebooks 01–07 | Ask before modifying |
| `outputs/` | CSV·PNG results saved by the notebooks | Ask before overwriting |
| `web/` | Local HTML results page | New files are fine; ask before changing existing ones |
| `reviews/` | Analysis review reports (Markdown) | Add new reports |

## Working rules
1. **Ask before modifying or deleting existing files.** This covers notebooks, `outputs/`, `data/`, `README.md`, and any files the user added. Only files you created in the current task may be changed without asking.
2. **Do not overstate causality.** Distinguish simple price changes, statistical association, predictive performance, and assumption-based scenarios. Write "rose because of ~" only when the analysis method supports it.
3. **Do not call external APIs.** Do not run the Google Routes API cells in notebook 05; use the saved public-transit travel-time CSV instead.
4. **Re-run notebooks only on copies.** Copy them to a temporary directory to run, and never overwrite the original notebooks or `outputs/`.
5. **Commit and push only when the user asks.** `main` is a protected branch that requires one approving review. Normally push to a new branch and open a PR; push directly to main only when the user says to.
6. **Ask before installing packages (`pip install`, etc.).**
7. **Do not give investment advice.** Do not use wording that recommends buying or selling in a specific area or complex.
8. Take numbers from `outputs/` results or notebook output. Never make them up.
9. Do not read, print, or commit secrets (`.env`, API keys).

## Conventions
- Write answers, documents, and notebook Markdown in **Korean**.
- Number new analysis notebooks **from 08** (`src/08_<topic>.ipynb`), and save their results in `outputs/08_<topic>/`.
- Save review reports as `reviews/<role>_<YYYY-MM-DD>.md`.
