import {Component, effect, inject, input, numberAttribute, OnInit, output, signal} from '@angular/core';
import {ProjectsService, ProjectI} from '../projects-service';
import {JsonPipe} from '@angular/common';
import {createStructuredContentOutput} from '@angular/cli/src/commands/mcp/utils';
import {LucideMenu, LucideSearch, LucideSettings, LucideSettings2} from '@lucide/angular';

@Component({
  selector: 'app-project',
  imports: [
    JsonPipe,
    LucideMenu,
    LucideSearch
  ],
  templateUrl: './project.html',
  styleUrl: './project.css',
})
export class Project {
  projectId = input.required({transform: numberAttribute})
  openNavLeftOutput = output()
  openNewProjectOutput = output()
  projectService = inject(ProjectsService)
  project = signal<null | ProjectI>(null)

  constructor() {
    effect(() => {
      const id = this.projectId();
      if (!id) return;
      this.projectService.getProjectById(id).subscribe(res => {
        this.project.set(res.isSuccess ? res.data : null);
      });
    });
  }



  openNavLeft() {
    this.openNavLeftOutput.emit()
  }

  openNewProject() {
    this.openNewProjectOutput.emit()
  }
}
