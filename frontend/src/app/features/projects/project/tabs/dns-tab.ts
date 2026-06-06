import {ChangeDetectionStrategy, Component, computed, input, signal} from '@angular/core';
import {DnsEntryI} from '../../projects-service';

@Component({
  selector: 'app-dns-tab',
  changeDetection: ChangeDetectionStrategy.OnPush,
  host: {class: 'flex flex-col flex-1 min-h-0'},
  template: `
    <div class="flex flex-col flex-1 min-h-0">
      <div class="flex gap-2 flex-wrap px-3 md:px-5 pt-3 md:pt-4">
        @for (t of types; track t) {
          <button type="button" class="badge" [class.cyan]="filter() === t"
                  style="cursor:pointer" (click)="filter.set(t)">{{ t }}</button>
        }
        <span class="flex-1"></span>
        <span class="mono self-center text-(--text-2)" style="font-size:11px">
          {{ rows().length }} record{{ rows().length === 1 ? '' : 's' }}
        </span>
      </div>
      <div class="flex-1 overflow-auto p-3 md:p-5">
        <div class="card overflow-hidden">
          <table class="dt">
            <thead>
              <tr>
                <th style="width:90px">Type</th>
                <th>Name</th>
                <th>Value</th>
                <th style="width:90px;text-align:right">TTL</th>
              </tr>
            </thead>
            <tbody>
              @for (r of rows(); track r.id) {
                <tr>
                  <td data-label="Type"><span [class]="'badge ' + color(r.type)">{{ r.type }}</span></td>
                  <td class="muted" data-label="Name">{{ r.domain }}</td>
                  <td style="word-break:break-all" data-label="Value">{{ r.value }}</td>
                  <td class="muted" style="text-align:right" data-label="TTL">{{ r.ttl }}</td>
                </tr>
              } @empty {
                <tr><td colspan="4" class="muted" style="text-align:center;padding:24px">No DNS records</td></tr>
              }
            </tbody>
          </table>
        </div>
      </div>
    </div>
  `,
})
export class DnsTab {
  entries = input<DnsEntryI[]>([]);
  filter = signal('ALL');
  types = ['ALL', 'A', 'AAAA', 'CNAME', 'MX', 'NS', 'TXT', 'CAA'];

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
