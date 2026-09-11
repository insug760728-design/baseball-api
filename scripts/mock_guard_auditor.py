#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Mock Guard Auditor (가짜 데이터 원천 차단 검증기)
Scans the entire codebase (.py, .html, .js) for fake data generators.
"""

import os
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

SEARCH_DIRS = ["app"]
EXTENSIONS = [".py", ".html", ".js"]

FORBIDDEN_PATTERNS = [
    (r"p_seed\s*=", "Seeded pseudo-random number generator (p_seed)"),
    (r"fallback_pool\s*=", "Fallback opponent pool used for fake match generation"),
    (r"opp_name\s*=\s*fallback_pool", "Selecting dummy opponent from fallback pool"),
    (r"team_score:\s*5,\s*opp_score:\s*3", "Hardcoded fake match score (5:3)"),
    (r"team_score:\s*86,\s*opp_score:\s*82", "Hardcoded fake basketball score"),
    (r"team_score:\s*2,\s*opp_score:\s*1", "Hardcoded fake soccer score array"),
    (r"bbSo\s*=\s*isHome\s*\?\s*['\"]3/8\s*:\s*2/7['\"]", "Hardcoded fake BB/SO boxscore string"),
    (r"starter\s*=\s*isHome\s*\?\s*['\"]6\.0이닝/1자", "Hardcoded fake starting pitcher boxscore string"),
    (r"err\s*=\s*isHome\s*\?\s*['\"]0\s*:\s*1['\"]", "Hardcoded fake errors boxscore string"),
    (r"lob\s*=\s*isHome\s*\?\s*['\"]6\s*:\s*5['\"]", "Hardcoded fake LOB boxscore string"),
    (r"round\(3\.20\s*\+\s*\(p_seed", "Fabricating pitcher ERA using p_seed formula"),
    (r"er_val\s*=\s*\[1,\s*0,\s*1\]", "Fabricating earned runs array"),
    (r"dec\s*=\s*\[['\"]승리투수\s*\(W\)['\"]", "Fabricating pitcher decision array"),
    (r"ip_v\s*=\s*\[['\"]6\.2['\"]", "Fabricating pitcher innings array"),
]

def scan_file(file_path):
    violations = []
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
            for line_no, line in enumerate(lines, 1):
                for pattern, desc in FORBIDDEN_PATTERNS:
                    if re.search(pattern, line):
                        violations.append({
                            "line": line_no,
                            "content": line.strip(),
                            "desc": desc
                        })
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    return violations

def run_audit(root_dir="."):
    total_files = 0
    total_violations = 0
    results = {}

    print(f"🔍 [Mock Guard Audit] Starting codebase scan in: {os.path.abspath(root_dir)}\n")

    for s_dir in SEARCH_DIRS:
        target_path = os.path.join(root_dir, s_dir)
        if not os.path.exists(target_path):
            continue
        for root, dirs, files in os.walk(target_path):
            if ".git" in root or "__pycache__" in root or "node_modules" in root:
                continue
            for f in files:
                if any(f.endswith(ext) for ext in EXTENSIONS) and not f.endswith(".bak"):
                    file_path = os.path.join(root, f)
                    total_files += 1
                    file_violations = scan_file(file_path)
                    if file_violations:
                        results[file_path] = file_violations
                        total_violations += len(file_violations)

    print("=" * 80)
    print(f"📊 [검사 결과] 총 검사 파일: {total_files}개 | 검출된 가짜 데이터 위반: {total_violations}건")
    print("=" * 80)

    if total_violations == 0:
        print("✅ [PASS] 코드베이스 내 모든 가짜 데이터 / Mock 생성기가 완전히 제거되었습니다.")
        return 0
    else:
        print("🚨 [FAIL] 가짜 데이터 생성기가 검출되었습니다:\n")
        for file_path, vios in results.items():
            rel_path = os.path.relpath(file_path, root_dir)
            print(f"📁 파일: {rel_path} ({len(vios)}건 검출)")
            for v in vios:
                print(f"   - [Line {v['line']:>5}] {v['desc']}")
                print(f"     코드: {v['content'][:100]}")
            print("-" * 80)
        return total_violations

if __name__ == "__main__":
    run_audit(".")
