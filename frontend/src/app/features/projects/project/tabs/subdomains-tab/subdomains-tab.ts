import {ChangeDetectionStrategy, Component, computed, input, signal} from '@angular/core';
import {LucideSearch} from '@lucide/angular';
import {SubdomainI} from '../../../projects-service';

@Component({
  selector: 'app-subdomains-tab',
  changeDetection: ChangeDetectionStrategy.OnPush,
  host: {class: 'flex flex-col flex-1 min-h-0'},
  imports: [LucideSearch],
  templateUrl: './subdomains-tab.html',
})
export class SubdomainsTab {
  subdomains = input<SubdomainI[]>([]);
  query = signal('');

  rows = computed(() => {
    const q = this.query().toLowerCase().trim();
    if (!q) return this.subdomains();
    return this.subdomains().filter(s =>
      s.name.toLowerCase().includes(q) || s.ip.includes(q));
  });

  onSearch(event: Event) {
    this.query.set((event.target as HTMLInputElement).value);
  }
}
