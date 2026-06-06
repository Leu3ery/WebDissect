import {ChangeDetectionStrategy, Component, computed, input, signal} from '@angular/core';
import {LucideSearch} from '@lucide/angular';
import {EndpointI} from '../../../projects-service';

@Component({
  selector: 'app-endpoints-tab',
  changeDetection: ChangeDetectionStrategy.OnPush,
  host: {class: 'flex flex-col flex-1 min-h-0'},
  imports: [LucideSearch],
  templateUrl: './endpoints-tab.html',
  styleUrl: './endpoints-tab.css',
})
export class EndpointsTab {
  endpoints = input<EndpointI[]>([]);
  query = signal('');

  rows = computed(() => {
    const q = this.query().toLowerCase().trim();
    if (!q) return this.endpoints();
    return this.endpoints().filter(e =>
      e.path.toLowerCase().includes(q) ||
      String(e.status).includes(q) ||
      e.method.toLowerCase().includes(q));
  });

  onSearch(event: Event) {
    this.query.set((event.target as HTMLInputElement).value);
  }

  methodColor(method: string): string {
    if (method === 'GET') return 'cyan';
    if (method === 'POST') return 'yellow';
    if (method === 'PUT') return 'violet';
    if (method === 'DELETE') return 'red';
    return 'gray';
  }

  statusDot(status: number): string {
    if (status >= 200 && status < 300) return 'green';
    if (status >= 400) return 'red';
    return 'gray';
  }

  statusColor(status: number): string {
    if (status >= 200 && status < 300) return 'var(--accent-2)';
    if (status >= 400) return 'var(--danger)';
    return 'var(--text-2)';
  }
}
