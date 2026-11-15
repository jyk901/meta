# -*- coding: utf-8 -*-
"""Mini NPU Simulator - MAC(Multiply-Accumulate) 연산으로 Cross / X 패턴을 판별한다.

외부 라이브러리 없이 표준 라이브러리(json, time, sys, os)만 사용한다.
"""
import json
import os
import sys
import time

EPSILON = 1e-9          # 점수 동점 판정 허용오차
REPEAT = 10             # 성능 측정 반복 횟수
LABEL_CROSS, LABEL_X = "Cross", "X"
DEFAULT_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.json")
LINE = "#" + "-" * 40


# ---------------------------------------------------------------- 라벨 정규화
def normalize_label(raw):
    """'+', 'cross' -> Cross / 'x' -> X (대소문자·공백 무시). 알 수 없으면 ValueError."""
    key = str(raw).strip().lower()
    if key in ("+", "cross"):
        return LABEL_CROSS
    if key == "x":
        return LABEL_X
    raise ValueError("알 수 없는 라벨: %r" % (raw,))


# ---------------------------------------------------------------- MAC 연산
def mac(pattern, flt):
    """같은 위치끼리 곱하고 모두 누적(Accumulate)한 점수를 반환 (반복문 직접 구현)."""
    n = len(pattern)
    total = 0.0
    for i in range(n):
        for j in range(n):
            total += pattern[i][j] * flt[i][j]
    return total


def mac_flat(pattern_flat, filter_flat):
    """[보너스] 1차원(길이 N²) 배열 버전: 인덱스 하나로 접근 패턴을 단순화."""
    total = 0.0
    for k in range(len(pattern_flat)):
        total += pattern_flat[k] * filter_flat[k]
    return total


def flatten(matrix):
    return [v for row in matrix for v in row]


def judge(score_a, score_b, label_a, label_b):
    """epsilon 기반 비교. 동점이면 UNDECIDED."""
    if abs(score_a - score_b) < EPSILON:
        return "UNDECIDED"
    return label_a if score_a > score_b else label_b


def measure_ms(func, *args, repeat=REPEAT):
    """연산 함수 호출 구간만 repeat회 측정해 평균(ms)과 마지막 결과를 반환 (I/O 제외)."""
    result = None
    start = time.perf_counter()
    for _ in range(repeat):
        result = func(*args)
    elapsed = time.perf_counter() - start
    return elapsed / repeat * 1000.0, result


# ---------------------------------------------------------------- 패턴 생성기 [보너스]
def make_cross(n):
    c = n // 2
    return [[1 if (i == c or j == c) else 0 for j in range(n)] for i in range(n)]


def make_x(n):
    return [[1 if (i == j or i + j == n - 1) else 0 for j in range(n)] for i in range(n)]


# ---------------------------------------------------------------- 모드 1: 사용자 입력
def read_matrix(title, n=3):
    """n줄 x n개 숫자를 입력받는다. 형식 오류 시 안내 후 처음부터 재입력."""
    while True:
        print("%s (%d줄 입력, 공백 구분)" % (title, n))
        rows, ok = [], True
        for _ in range(n):
            try:
                line = input().split()
            except EOFError:
                print("입력이 종료되었습니다.")
                sys.exit(1)
            if len(line) != n:
                ok = False
                print("입력 형식 오류: 각 줄에 %d개의 숫자를 공백으로 구분해 입력하세요." % n)
                break
            try:
                rows.append([float(tok) for tok in line])
            except ValueError:
                ok = False
                print("입력 형식 오류: 숫자만 입력할 수 있습니다.")
                break
        if ok:
            return rows


def fmt(v):
    return "%.1f" % v if abs(v - round(v)) < 1e-12 else repr(v)


def run_user_mode():
    print("\n" + LINE + "\n# [1] 필터 입력\n" + LINE)
    filt_a = read_matrix("필터 A")
    print()
    filt_b = read_matrix("필터 B")
    print("\n✓ 필터 A, B 저장 완료")
    print("\n" + LINE + "\n# [2] 패턴 입력\n" + LINE)
    pattern = read_matrix("패턴")

    ms_a, score_a = measure_ms(mac, pattern, filt_a)
    ms_b, score_b = measure_ms(mac, pattern, filt_b)
    result = judge(score_a, score_b, "A", "B")
    print("\n" + LINE + "\n# [3] MAC 결과\n" + LINE)
    print("A 점수: %s" % fmt(score_a))
    print("B 점수: %s" % fmt(score_b))
    print("연산 시간(평균/%d회): %.3f ms" % (REPEAT, (ms_a + ms_b) / 2))
    if result == "UNDECIDED":
        print("판정: 판정 불가 (|A-B| < %g)" % EPSILON)
    else:
        print("판정: %s" % result)
    print_perf_table([3])


# ---------------------------------------------------------------- 모드 2: data.json
def extract_size(key):
    """'size_13_2' -> 13. 형식이 틀리면 ValueError."""
    parts = key.split("_")
    if len(parts) != 3 or parts[0] != "size" or not parts[1].isdigit() or not parts[2].isdigit():
        raise ValueError("패턴 키 형식 오류: %r (size_{N}_{idx} 필요)" % key)
    return int(parts[1])


def is_square(m, n):
    return (isinstance(m, list) and len(m) == n and
            all(isinstance(r, list) and len(r) == n for r in m))


def load_filters(raw_filters):
    """filters -> {N: {Cross: matrix, X: matrix}}. 키는 라벨 정규화 적용."""
    filters = {}
    for size_key, group in raw_filters.items():
        n = extract_size(size_key + "_0")
        norm = {}
        for raw_label, matrix in group.items():
            label = normalize_label(raw_label)
            if not is_square(matrix, n):
                raise ValueError("%s 필터(%s)가 %dx%d 형태가 아님" % (size_key, raw_label, n, n))
            norm[label] = matrix
        if LABEL_CROSS not in norm or LABEL_X not in norm:
            raise ValueError("%s: Cross/X 필터가 모두 필요함" % size_key)
        filters[n] = norm
    return filters


def run_json_mode(path=DEFAULT_JSON):
    print("\n" + LINE + "\n# [1] 필터 로드\n" + LINE)
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        filters = load_filters(data["filters"])
        patterns = data["patterns"]
    except (OSError, ValueError, KeyError, TypeError) as e:
        print("✗ data.json 로드 실패: %s" % e)
        return
    for n in sorted(filters):
        print("✓ size_%d 필터 로드 완료 (Cross, X)" % n)

    print("\n" + LINE + "\n# [2] 패턴 분석 (라벨 정규화 적용)\n" + LINE)
    total, passed, failures = 0, 0, []
    for key, item in patterns.items():
        total += 1
        print("--- %s ---" % key)
        try:
            n = extract_size(key)
            if n not in filters:
                raise ValueError("size_%d 필터가 없음 (스키마 오류)" % n)
            pat = item["input"]
            if not is_square(pat, n):
                raise ValueError("입력 패턴 크기가 %dx%d와 불일치 (크기 불일치)" % (n, n))
            expected = normalize_label(item["expected"])
            s_cross = mac(pat, filters[n][LABEL_CROSS])
            s_x = mac(pat, filters[n][LABEL_X])
        except (ValueError, KeyError, TypeError) as e:
            reason = "스키마/크기 오류: %s" % e
            print("판정: 오류 | FAIL (%s)" % reason)
            failures.append((key, reason))
            continue
        result = judge(s_cross, s_x, LABEL_CROSS, LABEL_X)
        ok = result == expected
        print("Cross 점수: %s" % fmt(s_cross))
        print("X 점수: %s" % fmt(s_x))
        note = ""
        if not ok:
            reason = ("동점(UNDECIDED) 처리 규칙에 따라 FAIL" if result == "UNDECIDED"
                      else "판정 %s != expected %s" % (result, expected))
            failures.append((key, reason))
            note = " (%s)" % reason
        else:
            passed += 1
        print("판정: %s | expected: %s | %s%s" % (result, expected, "PASS" if ok else "FAIL", note))

    print_perf_table([3, 5, 13, 25], filters, patterns)
    print_optimization_table()

    print("\n" + LINE + "\n# [4] 결과 요약\n" + LINE)
    print("총 테스트: %d개\n통과: %d개\n실패: %d개" % (total, passed, len(failures)))
    if failures:
        print("\n실패 케이스:")
        for key, reason in failures:
            print("- %s: %s" % (key, reason))
    print("\n(상세 원인 분석 및 복잡도 설명은 README.md의 \"결과 리포트\" 섹션 참고)")


# ---------------------------------------------------------------- 성능 분석
def print_perf_table(sizes, filters=None, patterns=None):
    print("\n" + LINE + "\n# [3] 성능 분석 (평균/%d회)\n" % REPEAT + LINE)
    print("%-8s%-16s%s" % ("크기", "평균 시간(ms)", "연산 횟수(N²)"))
    print("-" * 40)
    for n in sizes:
        flt, pat = make_cross(n), make_x(n)   # 생성기 재사용 (I/O 없이 연산만 측정)
        if filters and n in filters:
            flt = filters[n][LABEL_CROSS]
        ms, _ = measure_ms(mac, pat, flt)
        print("%-8s%-16.3f%d" % ("%dx%d" % (n, n), ms, n * n))


def print_optimization_table(sizes=(3, 5, 13, 25), repeat=200):
    """[보너스] 2차원 vs 1차원 MAC: 동일 입력, 동일 반복 횟수로 비교 (변환 비용 제외)."""
    print("\n" + LINE + "\n# [보너스] 최적화 전/후 비교 (2D vs 1D, %d회 평균)\n" % repeat + LINE)
    print("%-8s%-14s%-14s%s" % ("크기", "2D(ms)", "1D(ms)", "속도 향상"))
    print("-" * 46)
    for n in sizes:
        p, f = make_x(n), make_cross(n)
        pf, ff = flatten(p), flatten(f)
        t2, r2 = measure_ms(mac, p, f, repeat=repeat)
        t1, r1 = measure_ms(mac_flat, pf, ff, repeat=repeat)
        assert abs(r1 - r2) < EPSILON        # 두 방식의 결과 동일성 검증
        print("%-8s%-14.4f%-14.4f%.2fx" % ("%dx%d" % (n, n), t2, t1, t2 / t1))


# ---------------------------------------------------------------- 진입점
def main():
    print("=== Mini NPU Simulator ===\n\n[모드 선택]\n")
    print("1. 사용자 입력 (3x3)\n2. data.json 분석")
    while True:
        try:
            choice = input("선택: ").strip()
        except EOFError:
            return
        if choice == "1":
            run_user_mode()
            return
        if choice == "2":
            run_json_mode(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_JSON)
            return
        print("1 또는 2를 입력하세요.")


if __name__ == "__main__":
    main()
