import {Component, inject, output} from '@angular/core';
import {ProjectsService} from '../projects-service';
import {LucidePlus, LucideSettings, LucideX} from '@lucide/angular';
import {AuthService} from '../../../core/services/auth-service';

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
  closeNavLeftOutput = output()


  closeNavLeft() {
    this.closeNavLeftOutput.emit()
  }

}
