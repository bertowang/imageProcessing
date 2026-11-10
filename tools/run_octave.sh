#!/usr/bin/env bash
# 批量验证全书 Octave 示例：不弹图形窗口，只检查能否正常结束并打印数值。
# 用法:
#   IP_HEADLESS=1 ./tools/run_octave.sh
#   IP_HEADLESS=1 ./tools/run_octave.sh part1/04-spatial-filter/code/04-linear-filter.m
set -u
cd "$(dirname "$0")/.." || exit 1

if ! command -v octave >/dev/null 2>&1; then
  echo "未找到 octave。请先安装 GNU Octave（macOS: brew install octave）。"
  echo "本书示例只用核心函数，不需要额外安装 image 包。"
  exit 1
fi

export IP_HEADLESS=1
tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT

if [ "$#" -gt 0 ]; then
  files=("$@")
else
  files=()
  while IFS= read -r f; do files+=("$f"); done < <(find part0 part1 part2 appendix -type f -name '*.m' | sort)
fi

pass=0
fail=0
for f in "${files[@]}"; do
  name="$(basename "$f")"
  if octave --no-gui --quiet "$f" >"$tmpdir/out" 2>&1; then
    first="$(grep -m1 -E '尺寸|min=|mean=|PSNR|阈值|连通域|====|grad|面积' "$tmpdir/out" | head -c 90)"
    printf 'OK   %-34s %s\n' "$name" "$first"
    pass=$((pass + 1))
  else
    printf 'FAIL %-34s\n' "$name"
    sed -n '1,8p' "$tmpdir/out" | sed 's/^/     /'
    fail=$((fail + 1))
  fi
done

printf '\n共 %d 个脚本：通过 %d，失败 %d\n' "${#files[@]}" "$pass" "$fail"
[ "$fail" -eq 0 ]
