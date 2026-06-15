import {ChangeDetectionStrategy, Component, computed, input} from '@angular/core';
import {SecurityCheckI} from '../../../projects-service';

@Component({
  selector: 'app-security-tab',
  changeDetection: ChangeDetectionStrategy.OnPush,
  host: {class: 'flex flex-col flex-1 min-h-0'},
  templateUrl: './security-tab.html',
})
export class SecurityTab {
  checks = input<SecurityCheckI[]>([]);

  fails = computed(() => this.checks().filter(c => c.status === 'fail').length);
  warns = computed(() => this.checks().filter(c => c.status === 'warn').length);
  oks = computed(() => this.checks().filter(c => c.status === 'ok').length);

  statusBadge(status: string): string {
    if (status === 'ok') return 'green';
    if (status === 'warn') return 'yellow';
    if (status === 'fail') return 'red';
    return 'gray';
  }

  severityBadge(severity: string): string {
    if (severity === 'high') return 'red';
    if (severity === 'medium') return 'yellow';
    if (severity === 'low') return 'violet';
    return 'gray';
  }
}
