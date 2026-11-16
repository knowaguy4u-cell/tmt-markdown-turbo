// Local harness compatibility: this host denies spawnSync pipes (EPERM).
// Redirect synchronous child streams through temporary regular files instead.
// This preload is used only by grade-local, never by the submitted driver.
const cp = require('node:child_process');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const original = cp.spawnSync;
cp.spawnSync = function(command, args, options = {}) {
  if (typeof options.stdio === 'string' && options.stdio !== 'pipe') return original(command, args, options);
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'md-spawn-'));
  const names = ['in', 'out', 'err'].map(x => path.join(dir, x));
  fs.writeFileSync(names[0], options.input ?? '');
  const fds = names.map((name, i) => fs.openSync(name, i ? 'w+' : 'r'));
  try {
    const result = original(command, args, { ...options, input: undefined, stdio: fds });
    result.stdout = fs.readFileSync(names[1], options.encoding || undefined);
    result.stderr = fs.readFileSync(names[2], options.encoding || undefined);
    result.output = [null, result.stdout, result.stderr];
    return result;
  } finally {
    fds.forEach(fd => fs.closeSync(fd));
    fs.rmSync(dir, { recursive: true, force: true });
  }
};
require('node:module').syncBuiltinESMExports();
