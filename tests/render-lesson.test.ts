import { describe, it, expect } from 'vitest';
// @ts-ignore -- plain-ESM export renderer under test
import {
  renderQuizHtml,
  renderGlossaryHtml,
  renderSourcesHtml,
} from '../scripts/lib/render-lesson.mjs';

describe('quiz static rendering (WordPress fallback)', () => {
  const quiz = {
    questions: [
      {
        question: 'What does a transistor act as?',
        options: ['A tiny switch', 'A power supply', 'A <script> tag', 'A display'],
        answer_index: 0,
        explanation: 'Billions of switches compose logic gates & circuits.',
      },
    ],
  };

  it('renders accessible details-based questions with the answer marked', () => {
    const html = renderQuizHtml(quiz);
    expect(html).toContain('<h2 id="quiz">Quiz</h2>');
    expect(html).toContain('<details>');
    expect(html).toContain('Answer: A.');
    expect(html).toContain('Q1. What does a transistor act as?');
  });

  it('escapes HTML in user-facing strings', () => {
    const html = renderQuizHtml(quiz);
    expect(html).toContain('A &lt;script&gt; tag');
    expect(html).not.toContain('<script>');
    expect(html).toContain('gates &amp; circuits');
  });

  it('renders nothing for an absent quiz', () => {
    expect(renderQuizHtml(null)).toBe('');
    expect(renderQuizHtml({ questions: [] })).toBe('');
  });
});

describe('glossary and sources rendering', () => {
  it('renders definition lists and citation lists', () => {
    const glossary = renderGlossaryHtml({
      terms: [{ term: 'bit', definition: 'A binary digit.' }],
    });
    expect(glossary).toContain('<dt><strong>bit</strong></dt>');
    const sources = renderSourcesHtml({
      sources: [
        {
          title: 'Von Neumann architecture',
          url: 'https://en.wikipedia.org/wiki/Von_Neumann_architecture',
          publisher: 'Wikipedia',
          accessed: '2026-07-12',
        },
      ],
    });
    expect(sources).toContain('href="https://en.wikipedia.org/wiki/Von_Neumann_architecture"');
    expect(sources).toContain('(accessed 2026-07-12)');
  });
});
