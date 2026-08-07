#!/bin/bash
# fault_distance.sh
# 輸入模型代號（例如 GRm366 GRm367 GRm368），依序執行：
#   1. draw_aps_dist_to_topo.py  -- 逐一計算每個模型的 aps_distance，存進各自資料夾
#   2. draw_aps_distance.py      -- 讀取上面存好的 aps_distance，畫跨模型比較圖
#
# 使用方式:
#   ./fault_distance.sh GRm366 GRm367 GRm368

set -e

if [ "$#" -eq 0 ]; then
    echo "usage: $0 <model_code1> [model_code2] ..."
    echo "example: $0 GRm366 GRm367 GRm368"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "============================================"
echo " Step 1: computing aps_distance per model"
echo "============================================"
python3 "$SCRIPT_DIR/draw_aps_dist_to_topo.py" "$@"

echo "============================================"
echo " Step 2: comparing aps_distance across models"
echo "============================================"
python3 "$SCRIPT_DIR/draw_aps_distance.py" "$@"

echo "============================================"
echo " Done."
echo "============================================"
