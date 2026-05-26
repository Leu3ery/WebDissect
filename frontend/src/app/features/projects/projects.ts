import {Component, OnDestroy, signal} from '@angular/core';
import {fromEvent, map} from 'rxjs';
import {Project} from './project/project';
import {NavLeft} from './nav-left/nav-left';

@Component({
  selector: 'app-projects',
  imports: [
    Project,
    NavLeft
  ],
  templateUrl: './projects.html',
  styleUrl: './projects.css',
})
export class Projects implements OnDestroy {
  isMobile = signal(window.innerWidth < 768);
  isNavLeftOpen = signal(false);
  private resizeSub = fromEvent(window, 'resize').pipe(
    map(() => window.innerWidth < 768)
  ).subscribe(v => this.isMobile.set(v));

  ngOnDestroy() {
    this.resizeSub.unsubscribe();
  }

  setNavLeft(state: boolean) {
    console.log(state);
    this.isNavLeftOpen.set(state)
  }
}
