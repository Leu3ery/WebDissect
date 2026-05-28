import {Component, inject, input, OnDestroy, OnInit, signal} from '@angular/core';
import {fromEvent, map} from 'rxjs';
import {Project} from './project/project';
import {NavLeft} from './nav-left/nav-left';
import {ProjectsService} from './projects-service';
import {AuthService} from '../../core/services/auth-service';
import {LucideKey, LucideLogOut} from '@lucide/angular';
import {Router} from '@angular/router';

@Component({
  selector: 'app-projects',
  imports: [
    Project,
    NavLeft,
    LucideKey,
    LucideLogOut
  ],
  templateUrl: './projects.html',
  styleUrl: './projects.css',
})
export class Projects implements OnDestroy, OnInit {
  authService = inject(AuthService);
  router = inject(Router);
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

  logout(): void {
    this.authService.logout()
    this.router.navigate(['login'])
  }
}
