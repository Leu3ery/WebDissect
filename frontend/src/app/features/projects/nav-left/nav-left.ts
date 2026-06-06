import {Component, inject, input, output} from '@angular/core';
import {ProjectsService} from '../projects-service';
import {LucidePlus, LucideSettings, LucideX} from '@lucide/angular';
import {AuthService} from '../../../core/services/auth-service';
import {Router} from '@angular/router';

@Component({
  selector: 'app-nav-left',
  imports: [
    LucideX,
    LucidePlus,
    LucideSettings
  ],
  templateUrl: './nav-left.html',
  styleUrl: './nav-left.css',
})
export class NavLeft {
  projectService = inject(ProjectsService)
  authService = inject(AuthService)
  router = inject(Router);
  closeNavLeftOutput = output()
  openSettingsOutput = output()
  openNewProject = output()
  projectId = input()
  projectsError = input('')


  closeNavLeft() {
    this.closeNavLeftOutput.emit()
  }

  openSettings() {
    this.openSettingsOutput.emit()
    this.closeNavLeft()
  }

  openProject(id: number) {
    this.router.navigate(['/projects/' + id]);
    this.closeNavLeft()
  }
}
