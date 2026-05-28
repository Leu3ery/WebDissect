import {Component, inject, input, OnDestroy, OnInit, signal} from '@angular/core';
import {fromEvent, map} from 'rxjs';
import {Project} from './project/project';
import {NavLeft} from './nav-left/nav-left';
import {ProjectsService} from './projects-service';

@Component({
  selector: 'app-projects',
  imports: [
    Project,
    NavLeft
  ],
  templateUrl: './projects.html',
  styleUrl: './projects.css',
})
export class Projects implements OnDestroy, OnInit {
  isMobile = signal(window.innerWidth < 768);
  isNavLeftOpen = signal(false);
  isSettingsOpen = signal(false);
  projectId = input()
  private resizeSub = fromEvent(window, 'resize').pipe(
    map(() => window.innerWidth < 768)
  ).subscribe(v => this.isMobile.set(v));
  projectService = inject(ProjectsService)

  ngOnInit(): void {
    this.projectService.getProjects().subscribe()
  }

  ngOnDestroy() {
    this.resizeSub.unsubscribe();
  }

  setNavLeft(state: boolean) {
    this.isNavLeftOpen.set(state)
  }

  setSettingsOpen(state: boolean) {
    this.isSettingsOpen.set(state)
  }
}
