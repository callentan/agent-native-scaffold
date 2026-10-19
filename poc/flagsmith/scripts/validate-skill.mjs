import assert from 'node:assert/strict';
import { existsSync, readdirSync, readFileSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const skipped = new Set(['.git', 'node_modules', 'dist', 'bin', 'obj']);
const files = [];
function walk(directory) {
  for (const entry of readdirSync(directory, { withFileTypes: true })) {
    if (skipped.has(entry.name)) continue;
    const absolute = path.join(directory, entry.name);
    if (entry.isDirectory()) walk(absolute);
    else if (/\.(md|json|ya?ml|ps1|ts|cs)$/.test(entry.name)) files.push(absolute);
  }
}
walk(root);

const failures = [];
function check(name, action) {
  try {
    action();
    console.log(`PASS: ${name}`);
  } catch (error) {
    if (!(error instanceof assert.AssertionError)) throw error;
    failures.push(name);
    console.error(`FAIL: ${name}: ${error.message}`);
  }
}

for (const file of files) {
  const relative = path.relative(root, file);
  const content = readFileSync(file, 'utf8');
  check(`English text: ${relative}`, () => {
    assert(!/\p{Script=Han}/u.test(content), 'Chinese text remains');
  });
  if (!file.endsWith('.md')) continue;
  check(`Local links: ${relative}`, () => {
    for (const match of content.matchAll(/\[[^\]]*\]\(([^)\s]+)\)/g)) {
      const target = match[1];
      if (/^(?:https?:|mailto:|#)/.test(target)) continue;
      const [targetPath, anchor] = target.split('#');
      const absolute = path.resolve(path.dirname(file), decodeURIComponent(targetPath).replaceAll('/', path.sep));
      assert(existsSync(absolute), `Missing link target: ${target}`);
      if (!anchor || !absolute.endsWith('.md')) continue;
      const headings = [...readFileSync(absolute, 'utf8').matchAll(/^#{1,6} (.+)$/gm)];
      const anchors = headings.map((heading) => heading[1].toLowerCase()
        .replace(/[^\p{L}\p{N}_\-\s]/gu, '').replace(/\s/g, '-'));
      assert(anchors.includes(anchor), `Missing heading: ${target}`);
    }
  });
  check(`Shell examples: ${relative}`, () => {
    assert(!/```(?:sh|bash)\b/.test(content), 'Use explicitly labeled PowerShell examples');
    assert(!/\\\r?\n\s+@(?:openfeature|flagsmith)/.test(content), 'Bash line continuation remains');
  });
}

const skillRoot = path.join(root, '.github', 'skills', 'openfeature-flagsmith-dotnet');
check('Skill discovery metadata', () => {
  const content = readFileSync(path.join(skillRoot, 'SKILL.md'), 'utf8');
  const frontmatter = content.match(/^---\r?\n([\s\S]+?)\r?\n---/);
  assert(frontmatter, 'Missing YAML frontmatter');
  assert(frontmatter[1].length <= 1024, 'Frontmatter exceeds the authoring budget');
  assert(/^name: openfeature-flagsmith-dotnet$/m.test(frontmatter[1]), 'Unexpected skill name');
  assert(/^description: Use when /m.test(frontmatter[1]), 'Description must state English trigger conditions');
  assert(content.split(/\r?\n/).length < 200, 'Keep the entry point concise');
  assert(content.trim().split(/\s+/).length <= 500, 'Keep the entry point within 500 words');
});
for (const required of [
  'examples/angular/feature-session.service.ts',
  'examples/angular/feature-session.spec.ts',
  'examples/dotnet/LocalEvaluation.cs',
  'examples/dotnet/Program.cs',
  'evals/scenarios.json',
  'evals/README.md'
]) {
  check(`Reusable support: ${required}`, () => assert(existsSync(path.join(skillRoot, required))));
}

if (failures.length) {
  console.error(`${failures.length} check(s) failed.`);
  process.exitCode = 1;
} else {
  console.log('All skill structure, English-language, link, and shell checks passed.');
}
