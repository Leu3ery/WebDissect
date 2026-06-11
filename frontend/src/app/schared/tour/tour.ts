import {ChangeDetectionStrategy, Component, computed, effect, inject, signal} from '@angular/core';
import {LucideX} from '@lucide/angular';
import {TourService} from './tour-service';

interface Box {
  top: number;
  left: number;
  width: number;
  height: number;
}

const CARD_WIDTH = 340;
const CARD_HEIGHT_EST = 220;
const GAP = 14;
const MARGIN = 16;
const PAD = 6;

@Component({
  selector: 'app-tour',
  imports: [LucideX],
  templateUrl: './tour.html',
  styleUrl: './tour.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
  host: {
    '(window:resize)': 'refresh()',
    '(window:scroll)': 'refresh()',
    '(document:keydown.escape)': 'tour.skip()',
    '(document:keydown.arrowRight)': 'tour.next()',
    '(document:keydown.arrowLeft)': 'tour.prev()',
  },
})
export class Tour {
  readonly tour = inject(TourService);

  /** Bumped whenever a re-measure of the target is needed. */
  private readonly version = signal(0);

  /** Bounding box of the current target element, or null for a centered card. */
  readonly hole = computed<Box | null>(() => {
    this.version();
    if (!this.tour.active()) {
      return null;
    }
    const selector = this.tour.current()?.target;
    if (!selector) {
      return null;
    }
    const el = document.querySelector(selector);
    if (!el) {
      return null;
    }
    const r = el.getBoundingClientRect();
    if (r.width === 0 && r.height === 0) {
      return null; // hidden element (e.g. collapsed mobile drawer)
    }
    return {
      top: r.top - PAD,
      left: r.left - PAD,
      width: r.width + PAD * 2,
      height: r.height + PAD * 2,
    };
  });

  /** Position of the tooltip card; null means render it centered. */
  readonly card = computed<{top: number; left: number} | null>(() => {
    const h = this.hole();
    if (!h) {
      return null;
    }
    const vw = window.innerWidth;
    const vh = window.innerHeight;
    const left = Math.min(Math.max(h.left, MARGIN), vw - CARD_WIDTH - MARGIN);

    let top: number;
    if (h.top + h.height + GAP + CARD_HEIGHT_EST <= vh - MARGIN) {
      top = h.top + h.height + GAP; // below target
    } else if (h.top - GAP - CARD_HEIGHT_EST >= MARGIN) {
      top = h.top - GAP - CARD_HEIGHT_EST; // above target
    } else {
      top = Math.min(Math.max(MARGIN, h.top), vh - CARD_HEIGHT_EST - MARGIN);
    }
    return {top, left};
  });

  constructor() {
    // When the step changes, scroll the target into view and re-measure.
    effect(() => {
      this.tour.index();
      if (!this.tour.active()) {
        return;
      }
      const selector = this.tour.current()?.target;
      setTimeout(() => {
        if (selector) {
          document
            .querySelector(selector)
            ?.scrollIntoView({block: 'center', inline: 'center', behavior: 'smooth'});
        }
        this.refresh();
        // Second pass after the smooth scroll settles.
        setTimeout(() => this.refresh(), 280);
      });
    });
  }

  refresh(): void {
    this.version.update((v) => v + 1);
  }
}
