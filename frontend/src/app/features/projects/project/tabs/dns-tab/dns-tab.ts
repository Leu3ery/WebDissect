import {ChangeDetectionStrategy, Component, computed, input, signal} from '@angular/core';
import {DnsEntryI} from '../../../projects-service';

@Component({
  selector: 'app-dns-tab',
  changeDetection: ChangeDetectionStrategy.OnPush,
  host: {class: 'flex flex-col flex-1 min-h-0'},
  templateUrl: './dns-tab.html',
  styleUrl: './dns-tab.css',
})
export class DnsTab {
  entries = input<DnsEntryI[]>([]);
  filter = signal('ALL');
  types = ['ALL', 'A', 'AAAA', 'CNAME', 'MX', 'NS', 'SOA', 'SRV', 'TXT', 'CAA'];

  rows = computed(() => {
    const f = this.filter();
    return this.entries().filter(r => f === 'ALL' || r.type === f);
  });

  color(type: string): string {
    if (type === 'A' || type === 'AAAA') return 'cyan';
    if (type === 'MX') return 'yellow';
    if (type === 'NS') return 'violet';
    if (type === 'TXT') return 'green';
    return 'gray';
  }
}
