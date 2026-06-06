import {ChangeDetectionStrategy, Component, input} from '@angular/core';
import {LucideCheck, LucideChevronRight, LucideShieldCheck} from '@lucide/angular';
import {CertificateI} from '../../../projects-service';

@Component({
  selector: 'app-ssl-tab',
  changeDetection: ChangeDetectionStrategy.OnPush,
  host: {class: 'flex flex-col flex-1 min-h-0'},
  imports: [LucideShieldCheck, LucideCheck, LucideChevronRight],
  templateUrl: './ssl-tab.html',
  styleUrl: './ssl-tab.css',
})
export class SslTab {
  certificates = input<CertificateI[]>([]);

  readonly k = 'mono uppercase tracking-wider text-(--text-2) text-[11px] pt-0.5 whitespace-nowrap';
  readonly v = 'mono text-[12.5px] text-(--text)';

  daysLeft(c: CertificateI): number {
    const ms = new Date(c.valid_to).getTime() - Date.now();
    return Math.max(0, Math.ceil(ms / 86_400_000));
  }

  pct(c: CertificateI): number {
    const from = new Date(c.valid_from).getTime();
    const to = new Date(c.valid_to).getTime();
    const now = Date.now();
    if (to <= from) return 0;
    const remaining = ((to - now) / (to - from)) * 100;
    return Math.max(0, Math.min(100, remaining));
  }

  datePart(value: string): string {
    return value ? value.split('T')[0] : '';
  }
}
