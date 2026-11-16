from pathlib import Path
p=Path('parse.js')
s=p.read_text()
def change(old,new):
    global s
    assert s.count(old)==1,(old,s.count(old))
    s=s.replace(old,new)
change('var N=new WeakMap;', '')
change('function Ae(a,e){let t=fe(e),n=N.get(a);n?n.push(t):N.set(a,[t])}',
       'function Ae(a,e){(a.delimiterBoundsStack??=[]).push(fe(e))}')
change('function Ee(a){let e=N.get(a);e&&(e.pop(),e.length===0&&N.delete(a))}',
       'function Ee(a){a.delimiterBoundsStack.pop()}')
assert s.count('N.get(a)?.at(-1)')==2
s=s.replace('N.get(a)?.at(-1)', 'a.delimiterBoundsStack?.at(-1)')
change('function J(a,e=0){let t=e,n="";', 'function J(a,e=0){if(!a.includes("\t"))return a;let t=e,n="";')
# split with a limit still allocates an array and examines the line terminator.
# No newline is a valid whole first line, including an empty suffix.
change('let g=t[2].split(`\n`,1)[0]', 'let g=firstLine(t[2])')
change('f=e.split(`\n`,1)[0]', 'f=firstLine(e)')
change('let U=e.split(`\n`,1)[0]', 'let U=firstLine(e)')
# The list whitespace regexp need not run without a tab; spaces are unchanged.
change('g.replace(this.rules.other.leadingSpaceTab,v=>J(v,b))',
       '(g.includes("\t")?g.replace(this.rules.other.leadingSpaceTab,v=>J(v,b)):g)')
change('Z=f.replace(this.rules.other.leadingSpaceTab,me=>J(me))',
       'Z=f.includes("\t")?f.replace(this.rules.other.leadingSpaceTab,me=>J(me)):f')
change('return t=t.replace(this.tokenizer.rules.inline.anyPunctuationOutsideCode,',
       'if(/[\\\\`]/.test(t))t=t.replace(this.tokenizer.rules.inline.anyPunctuationOutsideCode,')
change('s:n),t=t.replace(this.tokenizer.rules.inline.blockSkip,',
       's:n);if(/[\\[`<]/.test(t))t=t.replace(this.tokenizer.rules.inline.blockSkip,')
change('".repeat(n.length-o-2)+"]"}),t=this.options.hooks?',
       '".repeat(n.length-o-2)+"]"});return t=this.options.hooks?')
# D's factories refer to grammar constants defined later in this generated file.
# Initialize after module evaluation, before any parse, rather than on first use.
change('function D(a){let e=[];return t=>{let n=Math.max(0,Math.min(3,t-1)),s=e[n];return s||(s=a(n),e[n]=s),s}}',
       'var initializeSyntax=[];function D(a){let e=[];initializeSyntax.push(()=>{for(let n=0;n<4;n++)e[n]=a(n)});return t=>e[Math.max(0,Math.min(3,t-1))]}')
s+='''
// Syntax-only tables: no input, tokens, links, HTML, or document state is retained.
function firstLine(source) {
  const end=source.indexOf("\\n");
  return end<0?source:source.slice(0,end);
}
for(const initialize of initializeSyntax) initialize();
initializeSyntax=null;
const listItemSyntax=new Map();
for(const marker of ["\\\\*","\\\\+","\\\\-","[*+-]","\\\\d{1,9}\\\\.","\\\\d{1,9}\\\\)"]){
  listItemSyntax.set(marker,T.listItemRegex(marker));
}
T.listItemRegex=marker=>listItemSyntax.get(marker);
'''
p.write_text(s)
