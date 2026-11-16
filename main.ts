// Render independently in input order; only directory overrides vary for local runs.
import { readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { parse } from './parse.js';

const input = process.env.MAKEFUN_INPUT_DIR ?? '/input';
const output = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
const cases = JSON.parse(readFileSync(join(input, 'cases.json'), 'utf8'));
const rendered = cases.map(({ markdown }) => parse(markdown));
writeFileSync(join(output, 'html.json'), JSON.stringify(rendered));
