# 00_정제: 정제 거래 자료와 동 단위 특징표

생성 노트북: `src/재검증/00_데이터정제.ipynb`. 원자료 행을 삭제하지 않고 플래그로 표시했다.
**이번 실행에서는 Google Routes API를 호출하지 않았다(API 수집하지 않음).** 통근시간은 저장된 CSV만 썼고, 통근시간이 없는 동은 62개다(`commute_missing_dongs.csv`).

## 파일
| 파일 | 내용 |
|---|---|
| `transactions.parquet` | 거래 547,735행(원자료와 같음), 1행=원자료 1행 |
| `dong_features.parquet` | 법정동 338행, 기본키 (`gu`, `dong`), 조인 키 `dong_id` |
| `dong_features_meta.csv` | 특징별 기준일·관측 가능 시점·백테스트 사용 가능 여부 |
| `flag_counts.csv` | 플래그별 행 수 |
| `commute_missing_dongs.csv` | 통근시간 결측 동 목록 |
| `dong_match_report.csv` | 동별 좌표·통근·단지정보 매칭 결과 |
| `academy_unassigned_by_gu.csv` | 구별 학원 동 미배정 비율 |

## transactions.parquet 컬럼
| 컬럼 | 설명 |
|---|---|
| row_id | 원자료 행 순서(0부터). 고유키 |
| src_no | 원자료 NO(다운로드 묶음마다 1부터 다시 시작, 고유키 아님) |
| gu, dong, dong_id | 구, 법정동, "<구> <법정동>" 조인 키 |
| dong_key_missing | 시군구에서 구·동을 읽지 못한 행(결과 0행) |
| complex_id | 단지 키 = 구\|법정동\|단지명\|번지 |
| complex_name, jibun, road_name | 단지명, 번지, 도로명 |
| area_m2, floor, build_year | 전용면적(㎡), 층, 건축년도 |
| price_manwon, price_eok | 거래금액(만원), 거래금액(억원) |
| ppa_manwon, log_ppa | ㎡당 가격(만원/㎡), 그 자연로그 |
| contract_date, contract_ym, contract_year | 계약일, 계약월(YYYY-MM), 계약연도 |
| age | 계약연도 − 건축년도(음수 가능) |
| area_bin, age_bin, floor_bin | 분석용 구간(기준 범주: 060-085, 10-14, 06-10) |
| deal_type | 거래유형(중개/직거래). 2021-11 이후만 기록 |
| cancel_date, registration_date | 해제사유발생일, 등기일자(원문) |
| is_cancelled | 취소(해제) 거래 (17,606행) |
| cancel_unobserved | 계약월 < 2020-02: 취소 정보 자체가 없는 구간 (180,866행) |
| is_dup_exact | NO를 뺀 20개 열이 앞 행과 모두 같은 완전 중복(두 번째부터 표시, 4,506행) |
| bulk_n | 같은 단지·같은 계약일의 유효(취소·중복 제외) 거래 수 |
| is_bulk | 유효 거래 & bulk_n ≥ 10 (일괄 거래, 4,029행). 기준 근거는 노트북 2-3절 |
| is_partial_month | 2017-10(10-28부터), 2026-10(10-26까지) 부분 월 |
| is_recent_provisional | 2026-08, 2026-09: 취소·신고 지연이 끝나지 않은 잠정 월 |
| is_floor_nonpositive, is_age_negative, is_small_unit | 층 ≤ 0, 연식 < 0, 전용 20㎡ 미만 |
| price_robust_z, is_price_outlier | 구·연도 안 log(㎡당 가격) 로버스트 z, \|z\|>5 |
| is_direct_trade | 직거래 |
| in_base | 기본 표본: 취소 아님·완전 중복 아님·부분 월 아님·동 키 있음 (523,320행, 2017-11~2026-09) |
| in_base_nobulk | in_base & 일괄 거래 아님 (519,370행) |

## dong_features.parquet 컬럼
| 컬럼 | 설명 | 시점 |
|---|---|---|
| gu, dong, dong_id | 키 | - |
| lat, lon, coord_source, coord_n_points, coord_missing | 동 대표 좌표(단지 좌표 중앙값, 없으면 학교 좌표 중앙값) | 현재 단지 목록 |
| n_school_elem/middle/high/total | 초·중·고 학교 수(실제 0 포함) | **현재 시점** 2026-10-01 |
| acad_exam | 학원·교습소 중 분야 '입시.검정 및 보습' 수 | **현재 시점** |
| acad_exam_hagwon | acad_exam 중 '학원'만 | **현재 시점** |
| acad_lang / acad_arts / acad_other / acad_total | '국제화' / '예능(대)' / 그 밖의 분야 / 합계 | **현재 시점** |
| commute_gwanghwamun/gangnam/yeouido | 대중교통 통근시간(분), 구글 경로 | **현재 시점**, 출발 2026-11-18T08:00:00+09:00 |
| commute_min, commute_min_dest | 3곳 중 최솟값(분)과 해당 업무지구 | **현재 시점** |
| commute_missing | 통근 CSV에 없는 동(결측, 대체하지 않음) | - |
| subway_dist_m | 최근접 지하철역 거리(m, 단지별 값의 동 중앙값) | **현재 역 목록** |
| subway_n_1km | 반경 1km 역 수(동 중앙값) | **현재 역 목록** |
| nearest_transfer_share | 최근접 역이 환승역인 단지 비율 | **현재 역 목록** |
| bus_n_500m | 반경 500m 버스정류소 수(동 중앙값, 한강버스 제외) | **현재 정류소 목록** |
| gu_businesses_2024, gu_workers_2024 | **구 단위** 사업체 수·종사자 수(2024) | 2024년 |
| apt_n_complex, apt_households_median, apt_households_total, apt_large_share, apt_info_missing | 단지 수, 세대수 중앙값·합, 1,000세대 이상 단지 비율, 단지정보 결측 | **현재 단지 목록** |
| median_build_year, tx_n_base | 기본 표본 거래의 건축년도 중앙값, 거래 수 | 2017-11~2026-09 전체 |

## 인계 규칙(ml-engineer 포함)
1. 모든 조인은 `dong_id`로 한다. 동 이름만으로 조인하지 않는다.
2. `dong_features_meta.csv`에서 `usable_in_backtest=false`인 특징은 **현재 시점 횡단면 분석과 04·05의 연관 분석에만** 쓴다. **07-1 주 백테스트(워크포워드)에는 넣지 않는다.** 현재 `dong_features`의 모든 특징(동 대표 좌표 `lat`·`lon` 포함)이 false다. 좌표도 현재 단지·학교 목록으로 계산했기 때문이다.
3. 통근시간 결측 동은 대체하지 않는다. 쓰려면 결측 지시 변수(`commute_missing`)와 함께 쓰고, 결과에 결측 동 수를 적는다.
4. 학원 수 0은 "배정된 학원이 없음"이다. 괄호 주소가 없는 학원은 어느 동에도 배정되지 않았다.
5. 사업체·종사자는 구 단위 값이라 구 고정효과와 함께 쓰면 식별되지 않는다.
6. 기본 분석 표본은 `in_base`, 횡단면·패널 주결과는 `in_base_nobulk`를 권장한다. 2026-08~09는 잠정 월, 2020-02 이전은 취소 정보 없음.
