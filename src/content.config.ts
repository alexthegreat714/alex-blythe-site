import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

const sharedSchema = z.object({
  title: z.string(),
  summary: z.string(),
  date: z.coerce.date(),
  author: z.string().default('Alex Blythe'),
  tags: z.array(z.string()).default([]),
  readingTime: z.string(),
  draft: z.boolean().default(true),
  relatedSoftware: z.array(z.string()).default([]),
});

const research = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/research' }),
  schema: sharedSchema.extend({
    type: z.enum(['Technical note', 'Architecture', 'Benchmark', 'Test report', 'Paper', 'Failure analysis', 'Retrospective']),
  }),
});

const updates = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/updates' }),
  schema: sharedSchema.extend({
    product: z.string(),
    version: z.string().optional(),
    releaseUrl: z.string().url().optional(),
  }),
});

export const collections = { research, updates };

