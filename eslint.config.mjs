// @ts-check
import js from '@eslint/js';
import tseslint from 'typescript-eslint';

export default tseslint.config(
  {
    ignores: [
      'dist/**',
      '.astro/**',
      'node_modules/**',
      '**/*.astro', // .astro files are checked by `npm run typecheck` (astro check)
      'labs/**', // lab starter/example code is lesson material, linted by lab tests
      'instructor/**',
      // Python virtualenvs: installed packages ship their own JS (web workers,
      // notebook assets) which is vendor code, not ours. `.venv-tools/` is the
      // authoring environment for the Python tooling from Week 11 onward;
      // `.venv/` and `**/.venv/` are the per-lab environments learners create.
      '.venv-tools/**',
      '.venv/**',
      '**/.venv/**',
    ],
  },
  js.configs.recommended,
  ...tseslint.configs.recommended,
  {
    rules: {
      // Shared plain-ESM modules (scripts/lib/*.mjs) are imported from TS with
      // @ts-ignore; the import always lacks types, so expect-error would flap.
      '@typescript-eslint/ban-ts-comment': 'off',
    },
  },
  {
    files: ['scripts/**/*.mjs', 'curriculum/**/*.mjs'],
    languageOptions: {
      globals: {
        console: 'readonly',
        process: 'readonly',
        URL: 'readonly',
        fetch: 'readonly',
        setTimeout: 'readonly',
      },
    },
    rules: {
      'no-console': 'off',
    },
  },
);
