import { readFileSync } from 'node:fs';
import path from 'node:path';
import yaml from 'js-yaml';

export interface RepositoryConfig {
  mode: 'public';
  owner: string;
  /** The single repository that carries the whole course. */
  name: string;
  url: string;
  /** Where the "Star on GitHub" CTA points. Optional; falls back to `url`. */
  star_url?: string;
  branch: string;
  /** Retained aliases of name/url/branch so existing helpers keep working. */
  public_name: string;
  public_url: string;
  public_branch: string;
  site_branch: string;
}

export interface WebsiteConfig {
  local_base_url: string;
  public_base_url: string | null;
  base_path: string;
  port: number;
}

export interface CourseInfo {
  title: string;
  slug: string;
  days: number;
  weeks: number;
  language: string;
  author: string;
}

export interface CourseConfig {
  repository: RepositoryConfig;
  website: WebsiteConfig;
  course: CourseInfo;
}

export const repoRoot = path.resolve(process.cwd());

let cached: CourseConfig | null = null;

/** Loads config/course.config.yml — the single source of truth for URLs. */
export function loadConfig(): CourseConfig {
  if (!cached) {
    const raw = readFileSync(path.join(repoRoot, 'config', 'course.config.yml'), 'utf8');
    cached = yaml.load(raw) as CourseConfig;
  }
  return cached;
}
