"""재분석(src/재검증) 노트북 공통 함수.

- 경로는 노트북 첫 셀에서 정한 ROOT를 기준으로 상대 경로로 만든다.
- 회귀 함수는 numpy·scipy로 직접 구현했다(고정효과 흡수, 클러스터 표준오차, wild cluster bootstrap).
- 시계열 검정(ADF, HAC, VAR, Granger)은 statsmodels를 쓴다.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import scipy.sparse as sp

SEED = 42

SUMMARY_COLS = ["key", "label", "value", "unit", "sample_n", "period", "period_start",
                "period_end", "split_type", "claim_level", "source_file", "note"]
CLAIM_LEVELS = {"단순 변화", "통계적 연관", "예측 기여도", "가정 시나리오"}
SPLIT_TYPES = {"없음", "무작위", "그룹(단지)", "그룹(동)", "공간블록", "시간순", "워크포워드"}

AREA_REF, AGE_REF, FLOOR_REF = "060-085", "10-14", "06-10"


# ---------------------------------------------------------------- 입출력
def out_dir(root: Path, name: str) -> Path:
    d = Path(root) / "outputs" / "재검증" / name
    d.mkdir(parents=True, exist_ok=True)
    return d


def read_csv_any(path, **kw) -> pd.DataFrame:
    """utf-8-sig로 먼저 읽고, 실패하면 cp949로 읽는다."""
    for enc in ("utf-8-sig", "cp949"):
        try:
            return pd.read_csv(path, encoding=enc, **kw)
        except UnicodeDecodeError:
            continue
    raise UnicodeDecodeError("read_csv_any", b"", 0, 1, str(path))


def save_chart_csv(df: pd.DataFrame, outdir: Path, name: str) -> Path:
    if len(df) > 5000:
        raise ValueError(f"{name}: 차트 CSV는 5,000행 이하여야 합니다({len(df)}행)")
    p = Path(outdir) / name
    df.to_csv(p, index=False, encoding="utf-8-sig")
    return p


def save_summary(rows: list[dict], outdir: Path) -> pd.DataFrame:
    df = pd.DataFrame(rows)
    for c in SUMMARY_COLS:
        if c not in df.columns:
            df[c] = ""
    df = df[SUMMARY_COLS]
    bad_c = set(df["claim_level"]) - CLAIM_LEVELS
    bad_s = set(df["split_type"]) - SPLIT_TYPES
    if bad_c or bad_s:
        raise ValueError(f"허용되지 않는 값: {bad_c} {bad_s}")
    for c in ("period_start", "period_end"):
        ok = df[c].astype(str).str.fullmatch(r"\d{4}-\d{2}")
        if not ok.all():
            raise ValueError(f"{c} 형식 오류: {df.loc[~ok, 'key'].tolist()}")
    if df["key"].duplicated().any():
        raise ValueError("summary key 중복")
    df.to_csv(Path(outdir) / "summary.csv", index=False, encoding="utf-8-sig")
    return df


def save_meta(meta: dict, outdir: Path) -> None:
    with open(Path(outdir) / "meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)


def set_korean_font():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import font_manager
    names = {f.name for f in font_manager.fontManager.ttflist}
    for cand in ("AppleGothic", "NanumGothic", "Nanum Gothic", "Malgun Gothic"):
        if cand in names:
            plt.rcParams["font.family"] = cand
            break
    plt.rcParams["axes.unicode_minus"] = False
    plt.rcParams["figure.dpi"] = 100
    plt.rcParams["savefig.dpi"] = 100
    return plt


def save_png(fig, outdir: Path, name: str):
    """폭 1200px 이하로 저장한다(figsize 폭 ≤ 12인치, dpi 100)."""
    w, h = fig.get_size_inches()
    if w * 100 > 1200:
        fig.set_size_inches(12, h * 12 / w)
    fig.savefig(Path(outdir) / name, dpi=100, bbox_inches="tight")


# ---------------------------------------------------------------- 표본
def load_tx(root: Path, columns=None) -> pd.DataFrame:
    return pd.read_parquet(Path(root) / "outputs" / "재검증" / "00_정제" / "transactions.parquet",
                           columns=columns)


def ym_range(start: str, end: str) -> list[str]:
    return [p.strftime("%Y-%m") for p in pd.period_range(start, end, freq="M")]


# ---------------------------------------------------------------- 회귀 도구
def _codes(x) -> np.ndarray:
    return pd.factorize(pd.Series(x).astype(str), sort=True)[0]


def group_mean(values: np.ndarray, codes: np.ndarray, n_groups: int, w=None) -> np.ndarray:
    if w is None:
        cnt = np.bincount(codes, minlength=n_groups).astype(float)
        if values.ndim == 1:
            return np.bincount(codes, weights=values, minlength=n_groups) / cnt
        return np.column_stack([np.bincount(codes, weights=values[:, j], minlength=n_groups) / cnt
                                for j in range(values.shape[1])])
    raise NotImplementedError


def demean(M: np.ndarray, fe_codes: list[np.ndarray], tol=1e-9, maxit=500, copy=True) -> np.ndarray:
    """교대 사영(alternating projections)으로 여러 고정효과를 흡수한다."""
    M = np.array(M, dtype=float, copy=copy)
    ngs = [int(c.max()) + 1 for c in fe_codes]
    if len(fe_codes) == 1:
        M -= group_mean(M, fe_codes[0], ngs[0])[fe_codes[0]]
        return M
    for _ in range(maxit):
        delta = 0.0
        for c, ng in zip(fe_codes, ngs):
            gm = group_mean(M, c, ng)
            M -= gm[c]
            delta = max(delta, float(np.nanmax(np.abs(gm))))
        if delta < tol:
            break
    return M


def cluster_vcov(X: np.ndarray, e: np.ndarray, XtX_inv: np.ndarray, clusters: np.ndarray,
                 n_absorbed: int = 0):
    n, k = X.shape
    cl = _codes(clusters)
    G = int(cl.max()) + 1
    Gm = sp.csr_matrix((np.ones(n), (cl, np.arange(n))), shape=(G, n))
    S = np.asarray(Gm @ (X * e[:, None]))
    meat = S.T @ S
    c = G / (G - 1) * (n - 1) / max(n - k - n_absorbed, 1)
    return c * XtX_inv @ meat @ XtX_inv, G


def hc1_vcov(X, e, XtX_inv):
    n, k = X.shape
    meat = (X * e[:, None] ** 2).T @ X
    return n / (n - k) * XtX_inv @ meat @ XtX_inv


def fe_ols(y, X: pd.DataFrame, fe: list, clusters=None, demeaned=False, dof_absorbed=False):
    """y ~ X + 고정효과(흡수). 클러스터 표준오차. 결과 dict.

    dof_absorbed=True: 흡수한 고정효과 수를 소표본 보정과 t분포 자유도에 넣는다
    (관측 단위 = 클러스터 단위인 동 단위 회귀처럼 고정효과가 클러스터 안에 중첩되지 않을 때).
    """
    names = list(X.columns)
    yv = np.asarray(y, dtype=float)
    Xv = X.to_numpy(dtype=float)
    fe_codes = [_codes(f) for f in fe]
    if fe_codes and not demeaned:
        Z = demean(np.column_stack([yv, Xv]), fe_codes, copy=False)
        del Xv
        yd, Xd = Z[:, 0], Z[:, 1:]
    else:
        yd, Xd = yv, Xv
    # 흡수 후 상수열(변동 없음) 제거
    keep = (np.nanstd(Xd, axis=0) > 1e-10) | np.array([n == "const" for n in names])
    names = [n for n, k in zip(names, keep) if k]
    Xd = Xd[:, keep]
    XtX = Xd.T @ Xd
    XtX_inv = np.linalg.pinv(XtX)
    b = XtX_inv @ (Xd.T @ yd)
    e = yd - Xd @ b
    n_abs = sum(int(c.max()) + 1 for c in fe_codes)
    if fe_codes:
        n_abs -= 1  # 상수 하나는 고정효과에 흡수된 것으로 본다
    if clusters is not None:
        V, G = cluster_vcov(Xd, e, XtX_inv, np.asarray(clusters), n_absorbed=n_abs if dof_absorbed else 0)
    else:
        V, G = hc1_vcov(Xd, e, XtX_inv), None
    dof = (len(yd) - Xd.shape[1] - n_abs - 1) if dof_absorbed else ((G - 1) if G else (len(yd) - Xd.shape[1]))
    se = np.sqrt(np.diag(V))
    tss = float(((yd - yd.mean()) ** 2).sum())
    return {"names": names, "beta": pd.Series(b, index=names), "se": pd.Series(se, index=names),
            "vcov": pd.DataFrame(V, index=names, columns=names), "resid": e, "n": len(yd),
            "n_clusters": G, "r2_within": 1 - float((e ** 2).sum()) / tss if tss > 0 else np.nan,
            "Xd": Xd, "yd": yd, "XtX_inv": XtX_inv, "n_absorbed": n_abs, "fe_codes": fe_codes, "dof": dof,
            "dof_absorbed": dof_absorbed}


def coef_table(res, alpha=0.05) -> pd.DataFrame:
    from scipy import stats
    b, se = res["beta"], res["se"]
    dof = res["dof"]
    t = b / se
    p = 2 * stats.t.sf(np.abs(t), dof)
    q = stats.t.ppf(1 - alpha / 2, dof)
    return pd.DataFrame({"term": b.index, "coef": b.values, "se": se.values, "t": t.values,
                         "p_value": p, "ci_low": (b - q * se).values, "ci_high": (b + q * se).values})


def wild_cluster_boot_p(res, term: str, clusters, B=999, seed=SEED, refe=True):
    """제한 귀무(term 계수=0) Rademacher wild cluster bootstrap p값(양측, 대칭).

    refe=True(기본): 부호를 곱한 잔차로 만든 가상 종속변수를 매 반복마다 원래 모형과 같은
    고정효과로 다시 잔차화(demean)한 뒤 회귀·클러스터 공분산을 계산한다. 고정효과가 클러스터
    안에 중첩되지 않으면(예: 연월 FE와 동 클러스터) 부호 뒤집기로 고정효과 공간 성분이 생기므로
    이 단계가 필요하다. refe=False는 수정 전 방식으로, 합성 자료 비교용으로만 남겨 둔다.
    """
    names = res["names"]
    j = names.index(term)
    Xd, yd = res["Xd"], res["yd"]
    fe_codes = res.get("fe_codes") or []
    cl = _codes(clusters)
    G = int(cl.max()) + 1
    n, k = Xd.shape
    Gm = sp.csr_matrix((np.ones(n), (cl, np.arange(n))), shape=(G, n))
    # 제한 모형(고정효과를 흡수한 공간에서 추정)
    Xr = np.delete(Xd, j, axis=1)
    br = np.linalg.pinv(Xr.T @ Xr) @ (Xr.T @ yd)
    yhat_r = Xr @ br
    er = yd - yhat_r
    XtX_inv = res["XtX_inv"]
    c = G / (G - 1) * (n - 1) / max(n - k, 1)

    def tstat(yy):
        b = XtX_inv @ (Xd.T @ yy)
        e = yy - Xd @ b
        S = np.asarray(Gm @ (Xd * e[:, None]))
        V = c * XtX_inv @ (S.T @ S) @ XtX_inv
        return b[j] / np.sqrt(V[j, j])

    t_obs = tstat(yd)
    rng = np.random.default_rng(seed)
    cnt = 0
    for _ in range(B):
        w = rng.choice([-1.0, 1.0], size=G)
        ystar = yhat_r + w[cl] * er
        if refe and fe_codes:
            ystar = demean(ystar[:, None], fe_codes, tol=1e-10, copy=False)[:, 0]
        ts = tstat(ystar)
        cnt += abs(ts) >= abs(t_obs)
    return float((cnt + 1) / (B + 1)), float(t_obs)


def recover_two_fe(r: np.ndarray, c1: np.ndarray, c2: np.ndarray, tol=1e-10, maxit=2000):
    """r = a[c1] + b[c2] + e 에서 a, b를 교대 평균으로 구한다(b의 평균을 0으로 정규화하지 않음)."""
    n1, n2 = int(c1.max()) + 1, int(c2.max()) + 1
    a = np.zeros(n1)
    b = np.zeros(n2)
    for _ in range(maxit):
        a_new = group_mean(r - b[c2], c1, n1)
        b_new = group_mean(r - a_new[c1], c2, n2)
        d = max(np.max(np.abs(a_new - a)), np.max(np.abs(b_new - b)))
        a, b = a_new, b_new
        if d < tol:
            break
    return a, b


def dummies(df: pd.DataFrame, cols_refs: dict) -> pd.DataFrame:
    """범주형 열을 더미로 만들고 기준 범주를 뺀다."""
    out = []
    for col, ref in cols_refs.items():
        d = pd.get_dummies(df[col].astype(str), prefix=col, prefix_sep="=", dtype=float)
        refname = f"{col}={ref}"
        if refname in d.columns:
            d = d.drop(columns=refname)
        out.append(d)
    return pd.concat(out, axis=1)


CHAR_REFS = {"area_bin": AREA_REF, "age_bin": AGE_REF, "floor_bin": FLOOR_REF}
CHAR_REFS_NOAGE = {"area_bin": AREA_REF, "floor_bin": FLOOR_REF}


def time_dummy_index(d: pd.DataFrame, months: list[str], fe: str | None = "complex_id",
                     char_refs: dict | None = None, cluster: str = "complex_id", with_se=True):
    """월 더미 구성 보정 지수.

    log(㎡당 가격) ~ 월 더미 + 특성 구간 더미 + 고정효과(fe 흡수).
    반환: month, log_index(기준월=0), se, index(기준월=100), n.
    """
    if char_refs is None:
        char_refs = CHAR_REFS_NOAGE if fe == "complex_id" else CHAR_REFS
    d = d[d["contract_ym"].isin(months)]
    base = months[0]
    M = pd.get_dummies(pd.Categorical(d["contract_ym"], categories=months), dtype=float)
    M.columns = [f"m={c}" for c in months]
    M = M.drop(columns=f"m={base}")
    X = pd.concat([M.reset_index(drop=True), dummies(d, char_refs).reset_index(drop=True)], axis=1)
    y = d["log_ppa"].to_numpy()
    if fe is None:
        X.insert(0, "const", 1.0)
        res = fe_ols(y, X, [], clusters=d[cluster].to_numpy() if with_se else None)
    else:
        res = fe_ols(y, X, [d[fe].to_numpy()], clusters=d[cluster].to_numpy() if with_se else None)
    rows = [{"month": base, "log_index": 0.0, "se": 0.0}]
    for m in months[1:]:
        nm = f"m={m}"
        rows.append({"month": m, "log_index": float(res["beta"].get(nm, np.nan)),
                     "se": float(res["se"].get(nm, np.nan))})
    out = pd.DataFrame(rows)
    out["index"] = 100 * np.exp(out["log_index"])
    out = out.merge(d.groupby("contract_ym").size().rename("n").reset_index()
                    .rename(columns={"contract_ym": "month"}), on="month", how="left")
    return out, res


def dong_level(d: pd.DataFrame, char_refs: dict | None = None):
    """동 가격 수준: log(㎡당 가격) ~ 동 FE + 월 FE + 특성 구간 더미.

    반환: dong_id별 보정 로그 수준(서울 거래 가중 평균=0으로 중심화)과 거래 수.
    """
    char_refs = char_refs or CHAR_REFS
    X = dummies(d, char_refs).reset_index(drop=True)
    y = d["log_ppa"].to_numpy()
    c_dong = _codes(d["dong_id"])
    c_m = _codes(d["contract_ym"])
    res = fe_ols(y, X, [d["dong_id"].to_numpy(), d["contract_ym"].to_numpy()], clusters=None)
    r = y - X[res["names"]].to_numpy() @ res["beta"].to_numpy()
    a, b = recover_two_fe(r, c_dong, c_m)
    names = pd.Series(d["dong_id"].astype(str)).unique()
    labels = np.array(sorted(names))
    cnt = np.bincount(c_dong)
    lev = a - np.average(a, weights=cnt)
    return pd.DataFrame({"dong_id": labels, "adj_log_level": lev, "n_tx": cnt}), res


# ---------------------------------------------------------------- 공간
def haversine_m(lat1, lon1, lat2, lon2):
    R = 6371000.0
    p1, p2 = np.radians(lat1), np.radians(lat2)
    dphi = p2 - p1
    dl = np.radians(lon2) - np.radians(lon1)
    a = np.sin(dphi / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dl / 2) ** 2
    return 2 * R * np.arcsin(np.sqrt(a))


def knn_weights(lat, lon, k=5):
    lat, lon = np.asarray(lat), np.asarray(lon)
    D = haversine_m(lat[:, None], lon[:, None], lat[None, :], lon[None, :])
    np.fill_diagonal(D, np.inf)
    idx = np.argsort(D, axis=1)[:, :k]
    W = np.zeros_like(D)
    rows = np.repeat(np.arange(len(lat)), k)
    W[rows, idx.ravel()] = 1.0 / k
    return W


def morans_i(x, W, n_perm=999, seed=SEED):
    x = np.asarray(x, dtype=float)
    z = x - x.mean()
    n = len(z)
    S0 = W.sum()

    def stat(zz):
        return n / S0 * (zz @ W @ zz) / (zz @ zz)

    I = stat(z)
    rng = np.random.default_rng(seed)
    perm = np.array([stat(rng.permutation(z)) for _ in range(n_perm)])
    p = (np.sum(np.abs(perm - perm.mean()) >= abs(I - perm.mean())) + 1) / (n_perm + 1)
    return float(I), float(p), float(-1 / (n - 1))


def bh_fdr(p):
    p = np.asarray(p, dtype=float)
    n = len(p)
    order = np.argsort(p)
    q = np.empty(n)
    prev = 1.0
    for rank, i in reversed(list(enumerate(order, start=1))):
        prev = min(prev, p[i] * n / rank)
        q[i] = prev
    return q
