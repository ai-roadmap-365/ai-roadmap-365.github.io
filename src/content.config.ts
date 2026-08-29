import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

/**
 * Lessons live at content/sections/<section>/<subsection>/week-<nn>/day-<nnn>-<slug>/index.mdx.
 * Frontmatter carries only identity (day, title); all other metadata comes
 * from the sidecar YAML files loaded via src/lib/curriculum.ts.
 */
const lessons = defineCollection({
  loader: glob({ pattern: '**/day-*/index.mdx', base: './content/sections' }),
  schema: z.object({
    day: z.number().int().min(1).max(365),
    title: z.string(),
  }),
});

export const collections = { lessons };
