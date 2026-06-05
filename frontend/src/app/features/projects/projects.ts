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

@Component({
  selector: 'app-projects',
  imports: [
    Project,
    NavLeft,
    LucideKey,
    LucideLogOut,
    ChangePassword,
    NewProject,
    Settings
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
