# 재현성 점검 보고서 (2026-11-22)

## 요약
- 1차(깨끗한 빈 outputs) 실행 성공 **3/8** (01, 02, 06_정책_전후), 실패 5/8.
- 실패 5개의 원인은 두 가지:
  - 03, 04, 05: 설치된 `scipy 1.17.1`과 `statsmodels 0.14.4`가 호환되지 않아 `import statsmodels.formula.api`에서 ImportError. 코드 오류가 아니라 환경 문제. 설치·우회하지 않고 중단함. **이 3개는 실행·비교하지 못했다.**
  - 06_금리, 07: `outputs/06_policy/event_calendar.csv`가 없어 FileNotFoundError. 이 파일은 src/의 어떤 노트북도 만들지 않는다.
- 2차(원본 `outputs/06_policy/event_calendar.csv` 1개를 복사본에 넣고 06_금리, 07만 재실행): 둘 다 성공. 따라서 우회 포함 성공 **5/8**, 미실행 3/8(03·04·05).
- 결과 일치 **CSV 51개 / 불일치 0개**(02_analysis 28, 06_simple_before_after 9, 06_interest_panel 4, 07_model 10). 최대 절대 차이 0, 상대 차이 0(행·열·값 모두 동일). PNG 5개(02 2개, 06_simple 3개)는 생성 확인만 함.
- 03, 04, 05는 outputs 파일을 만들지 않고(화면 출력만) 실행도 못 해서 비교 대상이 없다.

## 실행 환경
- Python 3.13.5 (Anaconda, /opt/anaconda3), kernel `python3`
- pandas 3.0.3, numpy 2.4.6, scipy 1.17.1, statsmodels 0.14.4, scikit-learn 1.9.0, matplotlib 3.10.9, openpyxl 3.1.5, requests 2.32.3, nbconvert 7.16.6
- pandas 경고: numexpr 2.10.1 (pandas가 2.10.2 이상 요구)
- papermill 없음, `nbconvert --execute`(타임아웃 3600초, `MPLBACKEND=Agg`) 사용
- 복사본: `/private/tmp/claude-501/-Users-jujihun-Desktop-dev-property-estimate/ea5c2f73-710b-4db9-bcde-a7413d2a142e/scratchpad/review-repro/` (src, data 복사, outputs는 빈 폴더에서 시작). 원본 src/, outputs/, data/에는 쓰지 않았다.
- 노트북은 `root = cwd 또는 cwd.parent 중 data/가 있는 쪽`으로 경로를 잡아 복사본 루트를 가리켰다. 복사본의 src/에서 실행함.
- 복사본 변경점(원본은 그대로): 05번 6번 셀(Google Routes API 호출 셀)을 `저장된 CSV 읽기`만 하도록 교체. `.env`는 복사하지 않았다. 외부 네트워크 호출 없음.

## 노트북별 실행 결과
| 노트북 | 실행 | 소요 시간 | 비고 |
| --- | --- | --- | --- |
| 01_서울시_아파트_가격_추이_분석 | 성공 | 52초 | 파일 출력 없음(화면 출력만) |
| 02_급지별_상승률_선행후행_분석 | 성공 | 58초 | CSV 28개, PNG 2개 생성, 전부 일치 |
| 03_아파트_특성_가격_분석 | **실패** | 5초 | `ImportError: cannot import name '_lazywhere' from 'scipy._lib._util'` (statsmodels import 시점) |
| 04_학군_교육환경_가격_분석 | **실패** | 5초 | 위와 동일 |
| 05_직주근접_가격_분석 | **실패** | 5초 | 위와 동일. API 셀은 이미 제거한 상태에서도 실패 |
| 06_금리_가격_패널분석_보완 | 1차 실패 / 2차 성공 | 64초 / 54초 | 1차: `outputs/06_policy/event_calendar.csv` 없음. 2차: 원본 파일을 복사본에 넣고 성공 |
| 06_정책_전후_실거래가_단순비교 | 성공 | 80초 | CSV 9개, PNG 3개, 전부 일치. 원본 저장소에서 이 노트북은 미커밋 수정 상태(git status M)였고 수정본 기준으로 실행됨 |
| 07_가격전망_저평가_모델 | 1차 실패 / 2차 성공 | 58초 / 89초 | 06_금리와 같은 원인 |

## 결과 비교
허용 오차 1e-6. 비교 스크립트: `.../review-repro/compare.py`. 모든 CSV에서 행·열(컬럼명) 일치, 최대 절대 차이 0, 최대 상대 차이 0, 문자열 컬럼 동일. 06_금리와 07은 2차(event_calendar.csv 주입) 결과 기준.

| outputs 폴더 | 파일 수 | 행·열 일치 | 최대 차이 | 판정 |
| --- | --- | --- | --- | --- |
| 02_analysis | CSV 28 (+PNG 2 생성됨) | 전부 일치 | 0 (상대 0) | 일치 |
| 06_simple_before_after | CSV 9 (+PNG 3 생성됨) | 전부 일치 | 0 (상대 0) | 일치 |
| 06_interest_panel | CSV 4 | 전부 일치 | 0 (상대 0) | 일치 (event_calendar.csv 주입 조건) |
| 07_model | CSV 10 | 전부 일치 | 0 (상대 0) | 일치 (event_calendar.csv 주입 조건) |
| 02_k4_granger, 02_kmeans_review, 06_policy, apartment_matching | 각각 6, 4, 약 24, 2 | 비교 불가 | - | src/ 노트북 어느 것도 생성하지 않는 폴더. 재현 대상 아님 (지적 3 참고) |

개별 파일은 compare.py 출력(복사본 폴더) 참고. 03·04·05는 저장 결과가 outputs에 없어 비교 불가.

## 지적
| # | 심각도 | 위치 | 문제 | 근거 | 제안하는 수정 방향 |
| --- | --- | --- | --- | --- | --- |
| 1 | 치명 (현재 환경 기준 실행 불가) | 03, 04, 05 첫 import 셀 | 현재 환경에서 `statsmodels.formula.api` import 실패. 3개 노트북 재현 불가 | `scipy 1.17.1` + `statsmodels 0.14.4`에서 `_lazywhere` ImportError. 저장된 출력은 Python 3.13.5에서 생성됐으나 당시 패키지 버전은 기록이 없어 어떤 조합에서 만들었는지 알 수 없음. 02번에는 별도 statsmodels 호환 우회 코드가 있어 비슷한 문제를 이미 겪은 흔적이 있음 | 사용자 결정 필요. 후보: statsmodels를 scipy 1.17과 호환되는 새 버전으로 올리기 / scipy를 낮추기 / 가상환경 분리. 어느 쪽이든 새 버전에서 03~05 결과가 저장된 출력과 같은지 재확인 필요 |
| 2 | 치명 (깨끗한 환경에서 실행 불가) | 06_금리 3·9번 셀, 07 12번 셀 | 소스 노트북이 없는 `outputs/06_policy/event_calendar.csv`를 읽음 | 빈 outputs에서 두 노트북이 FileNotFoundError. `grep`상 src/ 노트북 중 이 파일을 만드는 것이 없음. README도 이전 DID·ITS 결과는 별도 보관이라고 적음 | event_calendar.csv를 생성하는 코드를 src/에 두거나, 입력 데이터로 `data/06_정책/`에 옮기고 노트북이 그쪽을 읽게 하기. 최소한 README 실행 순서에 선행 조건으로 명시 |
| 3 | 중요 | outputs/ 전체 | 02_k4_granger, 02_kmeans_review, 06_policy(DID·ITS 등), apartment_matching 폴더는 현재 src/ 노트북으로 재생성되지 않는 산출물 | 해당 폴더 파일이 1차·2차 실행 후에도 복사본에 하나도 생기지 않음 | 생성 코드의 위치를 문서화하거나, 보관용 폴더(archive)로 구분 |
| 4 | 중요 | 실행 순서 의존성 | 07은 `outputs/02_analysis/district_groups.csv`(02 결과)와 `06_policy/event_calendar.csv`를 읽고, 06_금리는 event_calendar.csv를 읽는다 | 02 이후 07 실행은 성공(이번 실행 순서가 01, 02, ... 07이어서 충족됨) | README에 02 -> 07 및 event_calendar 선행 관계를 명시 |
| 5 | 중요 | 패키지 버전 | requirements/환경 파일 없음. README도 "고정 버전 의존성 명세는 아직 제공하지 않습니다"라고 인정 | 프로젝트 루트에 requirements.txt, environment.yml 없음. 지적 1이 그 직접적 결과 | 현재 저장 결과를 만든 버전을 확인해 requirements.txt 또는 environment.yml로 고정 |
| 6 | 중요 | 05번 API 셀 | 외부 API 의존. 저장된 CSV(829행)를 읽는 것으로 이번엔 대체함. 원본 셀은 `.env`의 GOOGLE_MAPS_KEY가 있고 누락 건이 있으면 호출함 | 원본 셀은 cache에 없는 조합이 있을 때만 호출하고 상한 1000건이 있음. 호출 결과는 출발시각 기준 값이라 재호출 시 값이 달라질 수 있음 | 캐시 CSV를 입력 데이터로 고정한다고 문서화. API 셀은 별도 옵션 플래그로 분리 |
| 7 | 중요 | 03·04·05 (+07 일부) 랜덤성 | 03~05는 `random_state=42`(분할, RF, 샘플링, permutation)가 고정되어 있음. 02 K-means는 `random_state=42, n_init=50`. 07은 난수 사용 코드 없음 | 02 결과는 완전 일치(군집 포함). 03~05는 실행 못 해 확인 안 됨. RF는 `n_jobs=-1`이나 시드 고정이라 일반적으로 결정적이지만 scikit-learn 버전에 따라 달라질 수 있음 | 시드 고정은 양호. 지적 1 해결 후 03~05 수치를 저장 출력과 대조 |
| 8 | 사소 | 02번 셀 17 저장 출력 | 저장된 셀 출력에 절대 경로(`/Users/...`)가 남아 있음(경고 메시지 추정). 코드의 하드코딩 경로는 없음 | 코드 셀에서 `/Users/` 문자열 없음, 출력에만 있음 | 필요 시 출력 정리 |
| 9 | 사소 | 01 이외 모든 노트북 | 한글 폰트가 AppleGothic/Malgun/NanumGothic 중 있는 것을 쓰고 없으면 기본 폰트로 떨어짐. PNG는 환경에 따라 글자가 깨질 수 있음 | 노트북 폰트 선택 코드. 이번 환경은 macOS라 영향 확인하지 못함 | 선택 사항 |
| 10 | 사소 | 원본 작업 트리 | 06_정책_전후_실거래가_단순비교.ipynb가 미커밋 수정 상태 | git status `M` | 이번 결과는 수정본 기준으로 저장 결과와 일치. 커밋 전/후 결과가 같은지는 확인 안 함 |

## 사용자에게 묻고 싶은 것
1. 03·04·05가 막힌 것은 scipy 1.17.1 / statsmodels 0.14.4 비호환 때문이다. 설치·변경은 하지 않았다. 패키지 버전을 바꿔서(별도 가상환경) 다시 돌려도 되는가? 저장 결과를 만들 때 쓴 statsmodels·scipy 버전을 아는가?
2. event_calendar.csv는 어떤 노트북(또는 스크립트)이 만들었는가? src/에 없는 것이 의도인가?
3. 02_k4_granger, 02_kmeans_review, 06_policy, apartment_matching은 현재 재현 대상에서 제외해도 되는가?
4. 이번 2차 실행에서 원본 event_calendar.csv를 복사본에 넣은 것(원본은 읽기만 함)이 괜찮았는지, 앞으로도 같은 방식으로 해도 되는가?
