import {ChangeDetectionStrategy, Component, computed, input} from '@angular/core';
import {AnalysisRunI} from '../../../projects-service';

interface HistoryRow {
  id: number;
  time: string;
  kind: string;
  cells: {label: string; count: number; delta: number}[];
}

const CATS: {key: string; label: string}[] = [
  {key: 'dns', label: 'DNS'},
  {key: 'ssl', label: 'SSL'},
  {key: 'tech', label: 'Tech'},
  {key: 'subdomains', label: 'Subs'},
  {key: 'endpoints', label: 'Endpoints'},
  {key: 'ports', label: 'Ports'},
  {key: 'paths', label: 'Paths'},
  {key: 'security', label: 'Security'},
];

@Component({
  selector: 'app-history-tab',
  changeDetection: ChangeDetectionStrategy.OnPush,
  host: {class: 'flex flex-col flex-1 min-h-0'},
  templateUrl: './history-tab.html',
})
export class HistoryTab {
  runs = input<AnalysisRunI[]>([]);

  // runs come newest-first; delta is vs the next (older) run.
  rows = computed<HistoryRow[]>(() => {
    const runs = this.runs();
    return runs.map((run, i) => {
      const older = runs[i + 1];
      return {
        id: run.id,
        time: this.formatTime(run.created_at),
        kind: run.kind,
        cells: CATS.map(c => {
          const count = run.counts[c.key] ?? 0;
          const prev = older ? (older.counts[c.key] ?? 0) : count;
          return {label: c.label, count, delta: count - prev};
        }),
      };
    });
  });

  private formatTime(iso: string): string {
    const d = new Date(iso.endsWith('Z') || iso.includes('+') ? iso : iso + 'Z');
    return d.toLocaleString();
  }
}
