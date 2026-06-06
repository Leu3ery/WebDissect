import {ChangeDetectionStrategy, Component, input} from '@angular/core';
import {NgOptimizedImage} from '@angular/common';
import {TechnologyI} from '../../projects-service';

@Component({
  selector: 'app-tech-tab',
  changeDetection: ChangeDetectionStrategy.OnPush,
  host: {class: 'flex flex-col flex-1 min-h-0'},
  template: `
    <div class="flex-1 overflow-auto p-3 md:p-5">
      <div class="grid gap-3" style="grid-template-columns:repeat(auto-fill, minmax(min(100%, 220px), 1fr))">
        @for (t of technologies(); track t.id) {
          <div class="card flex items-center gap-3" style="padding:14px">
            <div class="flex items-center justify-center shrink-0 overflow-hidden"
                 style="width:38px;height:38px;border-radius:8px;background:var(--panel-3);border:1px solid var(--border)">
              @if (t.icon_url) {
                <img [ngSrc]="t.icon_url" [alt]="t.name" width="22" height="22" />
              } @else {
                <span class="mono" style="font-weight:700;font-size:13px;color:var(--accent)">{{ letter(t.name) }}</span>
              }
            </div>
            <div class="min-w-0 flex-1">
              <div style="font-weight:600;font-size:13.5px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{{ t.name }}</div>
              @if (t.description) {
                <div class="mono text-(--text-2)" style="font-size:11px;margin-top:2px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{{ t.description }}</div>
              }
            </div>
          </div>
        } @empty {
          <p class="muted" style="color:var(--text-2);font-size:13px">No technologies detected</p>
        }
      </div>
    </div>
  `,
  imports: [NgOptimizedImage],
})
export class TechTab {
  technologies = input<TechnologyI[]>([]);

  letter(name: string): string {
    return name.charAt(0).toUpperCase();
  }
}
