#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import json
from pathlib import Path

summary = json.loads(Path('summary.json').read_text())

tbl = [['' if j!=2 else '-'*5 for i in range(9)] for j in range(len(summary)+3)]

tbl[0][0] = "file"
tbl[1][0] = "file"
tbl[0][8] = "file"
tbl[1][8] = "file"
tbl[0][1] = "generated"
tbl[0][2] = "generated"
tbl[0][3] = "generated"
tbl[0][4] = "similarity"
tbl[0][5] = "final"
tbl[0][6] = "final"
tbl[0][7] = "final"
tbl[1][1] = "chars"
tbl[1][2] = "chars/line"
tbl[1][3] = "lines"
tbl[1][4] = "similarity"
tbl[1][5] = "lines"
tbl[1][6] = "chars/line"
tbl[1][7] = "chars"
for l, k in enumerate(summary.keys()):
    tbl[l+3][0] = k
    tbl[l+3][8] = k
    fmtint = "%d"
    fmtflt = "%.2f"
    tbl[l+3][1] = fmtint % summary[k]['generated']['chars']
    tbl[l+3][2] = fmtflt % summary[k]['generated']['chars_per_line']
    tbl[l+3][3] = fmtint % summary[k]['generated']['lines']
    tbl[l+3][4] = fmtflt % summary[k]['similarity']
    tbl[l+3][5] = fmtint % summary[k]['final']['lines']
    tbl[l+3][6] = fmtflt % summary[k]['final']['chars_per_line']
    tbl[l+3][7] = fmtint % summary[k]['final']['chars']
    tbl[l+3][4] += '%'

Path('summary.csv').write_text('\n'.join([','.join(ln) for ln in tbl]))
