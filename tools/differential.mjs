// Usage: node tools/differential.mjs <kit-directory>
// Temporary generated workloads stay outside the capped entry tree.
import assert from 'node:assert/strict';
import { readFileSync, writeFileSync, mkdirSync, mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { resolve, join } from 'node:path';
import { pathToFileURL } from 'node:url';
import { spawn } from 'node:child_process';
import { createHash } from 'node:crypto';
import { parse } from '../parse.js';
const kit=resolve(process.argv[2]);
const { marked }=await import(pathToFileURL(join(kit,'program/generator/vendor/marked/marked.esm.js')));
let counts={spec:0,practiceDocuments:0,generatedDocuments:0,random:0,targeted:0};
const digest=createHash('sha256');
function check(markdown, label, group) {
  const expected=marked.parse(markdown);
  const actual=parse(markdown);
  if(actual!==expected) {
    let at=0;while(at<actual.length&&at<expected.length&&actual[at]===expected[at])at++;
    console.error(JSON.stringify({label,markdown,at,actual,expected}));
    throw new Error(`Differential mismatch: ${label}`);
  }
  counts[group]++;digest.update(JSON.stringify([label,actual]));
}
const practice=JSON.parse(readFileSync(join(kit,'practice/input/cases.json'),'utf8'));
for(const c of practice) check(c.markdown,c.id,c.id.startsWith('doc-')?'practiceDocuments':'spec');
async function run(command,args,env) {
  await new Promise((ok,fail)=>{
    const child=spawn(command,args,{env,stdio:'inherit'});
    child.on('error',fail);child.on('exit',code=>code===0?ok():fail(new Error(`Generator exit ${code}`)));
  });
}
const scratch=mkdtempSync(join(tmpdir(),'md-differential-'));
try {
  for(let seedIndex=0;seedIndex<4;seedIndex++) {
    const input=join(scratch,'input'), output=join(scratch,`draw-${seedIndex}`);
    mkdirSync(input,{recursive:true});mkdirSync(output,{recursive:true});
    const seed=createHash('sha256').update(`authored-markdown-differential-${seedIndex}`).digest('hex');
    writeFileSync(join(input,'seed.json'),JSON.stringify({schema:'agent-fun/instance-seed/v1',seed}));
    await run(process.execPath,[join(kit,'program/generator/draw.ts')],{
      ...process.env,MAKEFUN_INPUT_DIR:input,MAKEFUN_OUTPUT_DIR:output
    });
    const cases=JSON.parse(readFileSync(join(output,'input/cases.json'),'utf8'));
    for(const c of cases.filter(c=>c.id.startsWith('doc-')))check(c.markdown,`seed-${seedIndex}/${c.id}`,'generatedDocuments');
  }
} finally {rmSync(scratch,{recursive:true,force:true});}
// Deterministic xorshift: all failures can be reproduced, with no test selection.
let state=0x7a63cd19;
function next(n){state^=state<<13;state^=state>>>17;state^=state<<5;return (state>>>0)%n;}
const pieces=[
  'plain words ', 'a_b_c', 'x**y**z', '*', '**', '***', '_', '__', '___', '~','~~',
  '`','``','```js\nx < y\n```','\\','\\*','\\\n','\n','\r','\r\n','\t','  ','   \n',
  '# h\n','> ','- ','+ ','* ','1. ','42) ','- [x] ','\n---\n','\n===\n',
  '[',']','(',')','![alt](x "title")','[a](b(c))','[a][ref]','[ref]: /target\n',
  '<a href="x">','</a>','<span>','</span>','<code>','</code>','<pre>','</pre>',
  '<!--','-->','<script>','</script>','<x y="z">','<http://example.org>',
  'http://a.example/x_(y)','HTTPS://a.example','ftp://a.example','www.a.example',
  'mailto:a@b.example','xmpp:a@b.example/x','a.b+c@d.example','@',':',
  '&amp;','&lt;','&#42;','&#95;','&#0;','&#x1F600;','&#xD800;','&bad;','&','<>',
  'café','日本語','😀','𝔘','\u0000','\u00a0','\u2028','\u0301','“','”','|a|b|\n|-|-|\n|c|d|'
];
for(let i=0;i<12000;i++) {
  let markdown='';const length=1+next(70);
  for(let j=0;j<length;j++)markdown+=pieces[next(pieces.length)];
  check(markdown,`random-${i}`,'random');
}
const targeted=[
  '', 'only text &#42; &#0; &amp; 😀', '*a* trailing text &#x80;',
  '<code>plain &amp; &#42;</code> trailing', '[a](b) suffix',
  '[x]: /one\n\n[x]', '[x]', '[x]: /two\n\n[x]',
  '***a **b _c_** d***', 'a_~b~_c', '  -\titem\n\tcontinued',
  '\tcode\r\n\r\ntext', '<pre>\n*raw*\n</pre>\n\nnormal',
];
for(let i=0;i<targeted.length;i++)check(targeted[i],`targeted-${i}`,'targeted');
// Repeat the first case after every other call to exercise isolation.
assert.equal(parse('[x]'),marked.parse('[x]'));
const report={node:process.version,counts,total:Object.values(counts).reduce((a,b)=>a+b,0),outputDigest:digest.digest('hex'),mismatches:0};
writeFileSync('evidence/differential.json',JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report,null,2));
