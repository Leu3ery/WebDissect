import {ChangeDetectionStrategy, Component, computed, input, signal} from '@angular/core';
import {LucideSearch} from '@lucide/angular';
import {PathEntryI} from '../../../projects-service';

@Component({
  selector: 'app-paths-tab',
  changeDetection: ChangeDetectionStrategy.OnPush,
  host: {class: 'flex flex-col flex-1 min-h-0'},
  imports: [LucideSearch],
  templateUrl: './paths-tab.html',
})
export class PathsTab {
  paths = input<PathEntryI[]>([]);
  query = signal('');

  rows = computed(() => {
    const q = this.query().toLowerCase().trim();
    if (!q) return this.paths();
    return this.paths().filter(p =>
      p.path.toLowerCase().includes(q) || String(p.status).includes(q));
  });

  onSearch(event: Event) {
    this.query.set((event.target as HTMLInputElement).value);
  }

  statusDot(status: number): string {
    if (status >= 200 && status < 300) return 'green';
    if (status >= 300 && status < 400) return 'gray';
    if (status >= 400) return 'red';
    return 'gray';
  }

  statusColor(status: number): string {
    if (status >= 200 && status < 300) return 'var(--accent-2)';
    if (status >= 400) return 'var(--danger)';
    return 'var(--text-2)';
  }
}
