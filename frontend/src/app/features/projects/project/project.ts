import {Component, effect, inject, input, numberAttribute, OnInit, output, signal} from '@angular/core';
import {ProjectsService, ProjectFullI} from '../projects-service';
import {JsonPipe} from '@angular/common';
import {LucideMenu, LucideSearch} from '@lucide/angular';

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
  project = signal<null | ProjectFullI>(null)

  constructor() {
    effect(() => {
      const id = this.projectId();
      if (!id) {
        this.project.set(null);
        return;
      }
      this.projectService.getProjectById(id).subscribe({
        next: res => this.project.set(res.isSuccess ? res.data : null),
        error: () => this.project.set(null),
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
