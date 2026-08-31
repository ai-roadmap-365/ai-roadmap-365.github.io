#!/usr/bin/env node
/**
 * Gate: a quiz must not be answerable without reading the lesson.
 *
 * Multiple-choice questions leak the answer through form rather than content.
 * Two leaks are measurable, and both were wide open across this course:
 *
 *   1. LENGTH. When the correct option carries the full explanation and the
 *      distractors are short dismissals, "pick the longest" beats reading. It
 *      scored 93% across 2,353 questions, against 25% by chance.
 *   2. POSITION. When the answer clusters at A/B, "always guess B" beats
 *      reading. It sat at 0 or 1 in 76% of questions.
 *
 * Neither says anything about whether the questions are good -- these ones are
 * well written. The reasoning simply belongs in the `explanation` field, which
 * every question already has and which the learner sees after answering.
 */
import { readFileSync, readdirSync, existsSync, statSync } from 'node:fs';
import path from 'node:path';
import yaml from 'js-yaml';

const BASE = 'content/sections';

// Chance is 1-in-4. Allowing half a file's questions to have the longest
// correct option leaves the strategy no better than guessing, without forcing
// artificial padding onto answers that are genuinely short.
const MAX_LONGEST_SHARE = 0.5;
// One position holding most of a file's answers is its own giveaway.
const MAX_POSITION_SHARE = 0.5;
// A correct option far longer than its nearest rival stands out on its own.
// Measured against the RUNNER-UP, not the mean: one deliberately short option
// ("0" beside three sentences) drags the mean down and makes a perfectly
// balanced question look like a giveaway.
const MAX_LENGTH_RATIO = 2.0;

const problems = [];
let files = 0;
let questions = 0;
let longestOverall = 0;

for (const section of readdirSync(BASE)) {
  const sp = path.join(BASE, section);
  if (!statSync(sp).isDirectory()) continue;
  for (const day of readdirSync(sp)
    .filter((d) => d.startsWith('day-'))
    .sort()) {
    const file = path.join(sp, day, 'quiz.yml');
    if (!existsSync(file)) continue;
    files += 1;
    const items = yaml.load(readFileSync(file, 'utf8'))?.questions ?? [];
    let longest = 0;
    const positions = new Map();

    for (const [i, q] of items.entries()) {
      const options = (q.options ?? []).map(String);
      const ai = q.answer_index;
      if (options.length < 2 || ai == null || !options[ai]) continue;
      questions += 1;

      const correct = options[ai].length;
      const others = options.filter((_, n) => n !== ai).map((s) => s.length);
      // Longer by a margin a reader could actually notice. Strict comparison
      // alone flags "flush" beside "file" -- one character among four-letter
      // keywords -- which nobody scans for, and chasing it costs real clarity
      // elsewhere. The margin scales, so it stays meaningful for long options.
      const runnerUp = Math.max(...others);
      if (correct - runnerUp >= Math.max(3, runnerUp * 0.1)) {
        longest += 1;
        longestOverall += 1;
      }
      positions.set(ai, (positions.get(ai) ?? 0) + 1);

      const ratio = correct / Math.max(runnerUp, 1);
      if (ratio > MAX_LENGTH_RATIO) {
        problems.push({
          file,
          kind: 'length',
          detail:
            `Q${i + 1}: correct option is ${ratio.toFixed(1)}x its longest distractor ` +
            `(${correct} chars vs ${runnerUp}) — move the reasoning into "explanation"`,
        });
      }
    }

    const n = items.length;
    if (!n) continue;
    if (longest / n > MAX_LONGEST_SHARE) {
      problems.push({
        file,
        kind: 'longest',
        detail: `${longest} of ${n} answers are the longest option — "pick the longest" beats reading`,
      });
    }
    for (const [pos, count] of positions) {
      if (count / n > MAX_POSITION_SHARE) {
        problems.push({
          file,
          kind: 'position',
          detail: `${count} of ${n} answers sit at index ${pos} — "always guess ${'ABCD'[pos]}" beats reading`,
        });
      }
    }
  }
}

const share = questions ? ((100 * longestOverall) / questions).toFixed(0) : '0';
console.log(
  `Quiz balance: ${files} quizzes, ${questions} questions. ` +
    `Answer is the longest option in ${longestOverall} (${share}%); chance is 25%.`,
);

if (!problems.length) {
  console.log('No quiz can be beaten by option length or position alone.');
  process.exit(0);
}
const byKind = new Map();
for (const p of problems) byKind.set(p.kind, [...(byKind.get(p.kind) ?? []), p]);
const EXPLAIN = {
  length: 'correct option far longer than its distractors',
  longest: '"pick the longest" beats reading the lesson',
  position: 'the answer clusters at one position',
};
for (const [kind, list] of byKind) {
  console.error(`\n${kind} — ${EXPLAIN[kind]} (${list.length})`);
  for (const p of list.slice(0, 8)) console.error(`  ${p.file}\n    ${p.detail}`);
  if (list.length > 8) console.error(`  ... and ${list.length - 8} more`);
}
console.error(
  `\n${problems.length} problems across ${new Set(problems.map((p) => p.file)).size} quizzes.`,
);
process.exit(1);
