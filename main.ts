// THE WORLD TODAY — the front page for Wednesday 18 November 2026,
// built for make.fun's news-image-20261118 bounty ($250 in USDC).
//
// The page itself is drawn by render.py (Python + Pillow) from
// stories.json and shipped in this repository as entry.png. This
// program's only job is to place that image where the grader looks
// for it, so the run is fully deterministic: the same bytes come out
// on every run, with no network, no randomness and no clock involved.
// Nothing is read from the environment except the output directory,
// and the copy is a plain file copy, so the result cannot vary.
//
// Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for
// /output:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
const source = fileURLToPath(new URL('./entry.png', import.meta.url));
const target = join(outDir, 'entry.png');

mkdirSync(dirname(target), { recursive: true });
copyFileSync(source, target);
