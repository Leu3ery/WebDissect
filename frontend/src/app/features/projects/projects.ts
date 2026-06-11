import {Component, inject, input, OnDestroy, OnInit, signal} from '@angular/core';
import {fromEvent, map} from 'rxjs';
import {Project} from './project/project';
import {NavLeft} from './nav-left/nav-left';
import {ProjectsService} from './projects-service';
import {AuthService} from '../../core/services/auth-service';
import {LucideKey, LucideLogOut} from '@lucide/angular';
import {Router} from '@angular/router';
import {ChangePassword} from './change-password/change-password';
import {NewProject} from './new-project/new-project';
import {Settings} from './settings/settings';
import {Tour} from '../../schared/tour/tour';
import {TourService} from '../../schared/tour/tour-service';

@Component({
  selector: 'app-projects',
  imports: [
    Project,
    NavLeft,
    LucideKey,
    LucideLogOut,
    ChangePassword,
    NewProject,
    Settings,
    Tour
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
  isNewProjectOpen = signal(false);
  isChangePasswordOpen = signal(false);
  projectsError = signal('');
  projectId = input()
  private resizeSub = fromEvent(window, 'resize').pipe(
    map(() => window.innerWidth < 768)
  ).subscribe(v => this.isMobile.set(v));
  projectService = inject(ProjectsService)
  private tourService = inject(TourService)

  ngOnInit(): void {
    this.projectService.getProjects().subscribe({
      next: res => {
        if (!res.isSuccess) {
          this.projectsError.set(res.message)
        }
      },
      error: () => this.projectsError.set('Could not load projects.'),
    })
    // Show the onboarding tour on first visit (no-op if already completed).
    this.tourService.start()
  }

  replayTour() {
    this.setSettingsOpen(false)
    this.setNavLeft(false)
    this.tourService.start(true)
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

  setChangePassword(state: boolean) {
    this.isChangePasswordOpen.set(state)
  }

  openChangePassword() {
    this.isChangePasswordOpen.set(true)
    this.setSettingsOpen(false)
    this.setNavLeft(false)
  }

  backFromChangePassword() {
    this.isChangePasswordOpen.set(false)
    this.setSettingsOpen(true)
  }

  logout(): void {
    this.authService.logout()
    this.router.navigate(['login'])
  }

  setNewProjectOpen(state: boolean) {
    this.isNewProjectOpen.set(state)
  }

  openNewProject() {
    this.isNewProjectOpen.set(true)
    this.setNavLeft(false)
  }

  closeNewProject() {
    this.isNewProjectOpen.set(false)
  }
}
