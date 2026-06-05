import {Component, inject, output, signal} from '@angular/core';
import {LucideKey, LucideUpload} from '@lucide/angular';
import {DecimalPipe} from '@angular/common';
import {FormBuilder, ReactiveFormsModule, Validators} from '@angular/forms';
import {ProjectCreate, ProjectsService} from '../projects-service';
import {Router} from '@angular/router';

@Component({
  selector: 'app-new-project',
  imports: [
    LucideUpload,
    DecimalPipe,
    ReactiveFormsModule,
  ],
  templateUrl: './new-project.html',
  styleUrl: './new-project.css',
})
export class NewProject {
  closeProject = output();
  selectedFile = signal<null | File>(null)
  projectService = inject(ProjectsService)
  router = inject(Router)
  error = signal('')

  fb = new FormBuilder();
  form = this.fb.group({
    name: ['', Validators.required],
    domain: ['', [Validators.required, Validators.pattern('([\\da-z.-]+)\\.([a-z.]{2,6})[/\\w .-]*/?')]],
    har: [''],
  })

  onFileChange(event: Event) {
    const input = event.target as HTMLInputElement;
    const file = input.files?.item(0)
    if (file) {
      this.selectedFile.set(file);
    }
  }

  getFileSize() {
    return this.selectedFile() != null ? this.selectedFile()!.size / 1000 / 1000 : 0
  }

  getFileName() {
    return this.selectedFile() != null ? this.selectedFile()!.name : 'no file';
  }

  createNewProject() {
    if (this.form.invalid) {
      return
    }

    const {name, domain} = this.form.getRawValue()
    const project: ProjectCreate = {
      name: name!,
      domain: domain!,
      har: this.selectedFile() ?? undefined,
    }
    this.projectService.createProject(project).subscribe(res => {
      if (!res.isSuccess) {
        this.error.set(res.message)
      } else {
        this.router.navigate(['/projects', res.data.id])
        this.closeProject.emit()
      }
    })
  }
}
