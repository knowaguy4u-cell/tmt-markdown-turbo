# Recorded first optimization pass, applied to the kit fork only.
from pathlib import Path
p = Path('parse.js')
s = p.read_text()
def change(old, new):
    global s
    assert s.count(old) == 1, (old, s.count(old))
    s = s.replace(old, new)
# Keep precedence; spaces retain every potentially indented block rule.
block = {'space':'/^[ \\t\\n]/', 'code':'/^[ \\t]/', 'fences':'/^[ `~]/',
         'heading':'/^[ #]/', 'hr':'/^[ *_-]/', 'blockquote':'/^[ >]/',
         'list':'/^[ *+0-9-]/', 'html':'/^[ <]/', 'def':'/^[ \\[]/'}
for method, test in block.items():
    change(f'if(r=this.tokenizer.{method}(e))', f'if({test}.test(e)&&(r=this.tokenizer.{method}(e)))')
inline = {'escape':'/^[\\\\]/', 'tag':'/^</', 'link':'/^[!\\[]/',
          'emStrong':'/^[*_]/', 'codespan':'/^`/', 'br':'/^[ \\\\]/',
          'del':'/^~/', 'autolink':'/^</'}
for method, test in inline.items():
    args = 'e,t,r' if method in ('emStrong','del') else 'e'
    change(f'if(i=this.tokenizer.{method}({args}))', f'if({test}.test(e)&&(i=this.tokenizer.{method}({args})))')
change('if(i=this.tokenizer.reflink(e,this.tokens.links))', 'if(/^[!\\[]/.test(e)&&(i=this.tokenizer.reflink(e,this.tokens.links)))')
change('if(!this.state.inLink&&(i=this.tokenizer.url(e)))', 'if(!this.state.inLink&&/^[A-Za-z0-9._+-]/.test(e)&&(i=this.tokenizer.url(e)))')
change('#e(e,t){let n=', '#e(e,t){if(!/[*_~]/.test(e))return this.#t(e,e,t);let n=')
# A whole remaining suffix is plain only if neither Markdown nor GFM URL/email
# recognition can split it. Numeric references still use marked's own decoder.
change('let i;if(this.options.extensions?.inline?', '''let i;
if(!/[\\\\<!\\[`*_~\\r\\n@:]|www\\./.test(e)){
  let rawBlock=this.state.inRawBlock;
  let text=rawBlock?e:Ie(e), previous=n.at(-1);
  if(previous?.type==="text"){previous.raw+=e;previous.text+=text;}
  else n.push({type:"text",raw:e,text,escaped:rawBlock});
  break;
}
if(this.options.extensions?.inline?''')
p.write_text(s)
