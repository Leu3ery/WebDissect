import {computed, Injectable, signal} from '@angular/core';

export interface TourStep {
  /** CSS selector of the element to highlight. Omit for a centered card. */
  target?: string;
  title: string;
  body: string;
}

const STORAGE_KEY = 'wd_tour_done_v1';

const STEPS: TourStep[] = [
  {
    title: 'Welcome to WebDissect 👋',
    body: 'This is a website reconnaissance tool: DNS records, SSL/TLS certificates, technologies and HTTP endpoints. Let\'s walk through the main features — it takes less than a minute.',
  },
  {
    target: '[data-tour="new-project"]',
    title: 'Create a project',
    body: 'Click here to add a project. All you need is a name and a domain (e.g. example.com). Optionally, you can attach a HAR file right away to analyze endpoints.',
  },
  {
    target: '[data-tour="projects-list"]',
    title: 'Your projects',
    body: 'All saved projects appear in this list. Clicking a project opens its results — they are stored, so you can come back anytime.',
  },
  {
    target: '[data-tour="upload-har"]',
    title: 'Upload a HAR',
    body: 'A HAR file (exported from the Network tab in DevTools) lets you extract the site\'s list of HTTP endpoints. Files up to 10 MB are supported.',
  },
  {
    target: '[data-tour="run-analysis"]',
    title: 'Run the analysis',
    body: 'The "Run Analysis" button collects fresh data: DNS records, the TLS certificate, technologies (from headers/HTML) and endpoints from the uploaded HAR files.',
  },
  {
    target: '[data-tour="tabs"]',
    title: 'Results by category',
    body: 'Switch between the DNS, Tech Stack, Endpoints and SSL/TLS tabs. The number next to each name shows how many records were found.',
  },
  {
    target: '[data-tour="settings"]',
    title: 'Account settings',
    body: 'Here you can change your password or log out. You can also restart this tour from the settings at any time.',
  },
  {
    title: 'All set! 🚀',
    body: 'Now you know the essentials. Create your first project and run an analysis. Happy digging!',
  },
];

@Injectable({providedIn: 'root'})
export class TourService {
  readonly steps = signal<TourStep[]>(STEPS);
  readonly index = signal(0);
  readonly active = signal(false);

  readonly current = computed(() => this.steps()[this.index()]);
  readonly isFirst = computed(() => this.index() === 0);
  readonly isLast = computed(() => this.index() === this.steps().length - 1);

  /** Start the tour. Skips automatically if already completed (unless forced). */
  start(force = false): void {
    if (!force && this.hasSeen()) {
      return;
    }
    this.index.set(0);
    this.active.set(true);
  }

  next(): void {
    if (this.isLast()) {
      this.finish();
    } else {
      this.index.update((i) => i + 1);
    }
  }

  prev(): void {
    if (!this.isFirst()) {
      this.index.update((i) => i - 1);
    }
  }

  skip(): void {
    this.finish();
  }

  private finish(): void {
    this.active.set(false);
    try {
      localStorage.setItem(STORAGE_KEY, '1');
    } catch {
      // localStorage may be unavailable (private mode) - ignore.
    }
  }

  private hasSeen(): boolean {
    try {
      return localStorage.getItem(STORAGE_KEY) === '1';
    } catch {
      return false;
    }
  }
}
