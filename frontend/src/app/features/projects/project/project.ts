import {Component, effect, inject, input, numberAttribute, output, signal} from '@angular/core';
import {ProjectsService, ProjectFullI} from '../projects-service';
import {LucideActivity, LucideGlobe, LucideLayers, LucideMenu, LucidePlay, LucideSearch, LucideShieldCheck, LucideUpload} from '@lucide/angular';
import {NotificationService} from '../../../schared/notifications/notification-service';
import {DnsTab} from './tabs/dns-tab/dns-tab';
import {TechTab} from './tabs/tech-tab/tech-tab';
import {EndpointsTab} from './tabs/endpoints-tab/endpoints-tab';
import {SslTab} from './tabs/ssl-tab/ssl-tab';

type TabId = 'dns' | 'tech' | 'ep' | 'ssl';

@Component({
  selector: 'app-project',
  imports: [
    LucideMenu,
    LucideSearch,
    LucideUpload,
    LucidePlay,
    LucideGlobe,
    LucideLayers,
    LucideActivity,
    LucideShieldCheck,
    DnsTab,
    TechTab,
    EndpointsTab,
    SslTab
  ],
  templateUrl: './project.html',
  styleUrl: './project.css',
})
export class Project {
  projectId = input.required({transform: numberAttribute})
  openNavLeftOutput = output()
  openNewProjectOutput = output()
  projectService = inject(ProjectsService)
  notifications = inject(NotificationService)
  project = signal<null | ProjectFullI>(null)
  uploading = signal(false)
  analyzing = signal(false)
  activeTab = signal<TabId>('dns')

  constructor() {
    effect(() => {
      const id = this.projectId();
      if (!id) {
        this.project.set(null);
        return;
      }
      this.loadProject(id);
    });
  }

  private loadProject(id: number) {
    this.projectService.getProjectById(id).subscribe({
      next: res => this.project.set(res.isSuccess ? res.data : null),
      error: () => this.project.set(null),
    });
  }

  onHarSelected(event: Event) {
    const input = event.target as HTMLInputElement;
    const file = input.files?.item(0);
    input.value = '';
    if (!file || this.uploading()) {
      return;
    }
    this.uploading.set(true);
    this.projectService.uploadHar(this.projectId(), file).subscribe({
      next: res => {
        this.uploading.set(false);
        if (!res.isSuccess) {
          this.notifications.error(res.message);
          return;
        }
        this.notifications.success('HAR file uploaded successfully.');
      },
      error: () => {
        this.uploading.set(false);
        this.notifications.error('Could not upload HAR file.');
      },
    });
  }

  runAnalysis() {
    if (this.analyzing()) {
      return;
    }
    const id = this.projectId();
    this.analyzing.set(true);
    this.projectService.startAnalysis(id).subscribe({
      next: res => {
        this.analyzing.set(false);
        if (!res.isSuccess) {
          this.notifications.error(res.message);
          return;
        }
        this.notifications.success('Analysis started.');
        this.loadProject(id);
      },
      error: () => {
        this.analyzing.set(false);
        this.notifications.error('Could not start analysis.');
      },
    });
  }

  openNavLeft() {
    this.openNavLeftOutput.emit()
  }

  openNewProject() {
    this.openNewProjectOutput.emit()
  }
}
