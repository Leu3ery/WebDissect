import {Component, effect, inject, input, numberAttribute, OnDestroy, output, signal} from '@angular/core';
import {Subscription} from 'rxjs';
import {ProjectsService, ProjectFullI} from '../projects-service';
import {AnalysisEvent, AnalysisSocketService, CategoryState} from '../analysis-socket';
import {
  LucideActivity, LucideFolderTree, LucideGlobe, LucideLayers, LucideLoaderCircle,
  LucideMenu, LucideNetwork, LucidePlay, LucideScanSearch, LucideSearch, LucideServer,
  LucideShieldCheck, LucideUpload, LucideCheck
} from '@lucide/angular';
import {NotificationService} from '../../../schared/notifications/notification-service';
import {DnsTab} from './tabs/dns-tab/dns-tab';
import {TechTab} from './tabs/tech-tab/tech-tab';
import {EndpointsTab} from './tabs/endpoints-tab/endpoints-tab';
import {SslTab} from './tabs/ssl-tab/ssl-tab';
import {SubdomainsTab} from './tabs/subdomains-tab/subdomains-tab';
import {PortsTab} from './tabs/ports-tab/ports-tab';
import {PathsTab} from './tabs/paths-tab/paths-tab';

type TabId = 'dns' | 'tech' | 'ep' | 'ssl' | 'subs' | 'ports' | 'paths';

@Component({
  selector: 'app-project',
  imports: [
    LucideMenu, LucideSearch, LucideUpload, LucidePlay, LucideGlobe, LucideLayers,
    LucideActivity, LucideShieldCheck, LucideNetwork, LucideServer, LucideFolderTree,
    LucideScanSearch, LucideLoaderCircle, LucideCheck,
    DnsTab, TechTab, EndpointsTab, SslTab, SubdomainsTab, PortsTab, PathsTab,
  ],
  templateUrl: './project.html',
  styleUrl: './project.css',
})
export class Project implements OnDestroy {
  projectId = input.required({transform: numberAttribute})
  openNavLeftOutput = output()
  openNewProjectOutput = output()
  projectService = inject(ProjectsService)
  private analysisSocket = inject(AnalysisSocketService)
  notifications = inject(NotificationService)
  project = signal<null | ProjectFullI>(null)
  uploading = signal(false)
  analyzing = signal(false)
  scanMenuOpen = signal(false)
  activeTab = signal<TabId>('dns')
  progress = signal<Record<string, CategoryState>>({})

  // Categories shown in the live progress strip, in display order.
  readonly progressCats = [
    {key: 'dns', label: 'DNS'},
    {key: 'ssl', label: 'SSL/TLS'},
    {key: 'tech', label: 'Tech'},
    {key: 'subdomains', label: 'Subdomains'},
    {key: 'endpoints', label: 'Endpoints'},
    {key: 'ports', label: 'Ports'},
    {key: 'paths', label: 'Paths'},
  ];

  private socketSub?: Subscription;

  constructor() {
    effect(() => {
      const id = this.projectId();
      this.openSocket(id);
      if (!id) {
        this.project.set(null);
        return;
      }
      this.loadProject(id);
    });
  }

  ngOnDestroy() {
    this.socketSub?.unsubscribe();
  }

  private openSocket(id: number) {
    this.socketSub?.unsubscribe();
    if (!id) return;
    this.socketSub = this.analysisSocket.connect(id).subscribe({
      next: ev => this.onEvent(id, ev),
      error: () => {/* socket dropped; UI keeps last known state */},
    });
  }

  private onEvent(id: number, ev: AnalysisEvent) {
    switch (ev.type) {
      case 'snapshot':
        this.progress.set(ev.categories ?? {});
        this.analyzing.set(!!ev.running);
        break;
      case 'start':
        this.analyzing.set(true);
        break;
      case 'progress':
        if (ev.category) {
          this.progress.update(p => ({
            ...p,
            [ev.category!]: {status: ev.status ?? 'running', count: ev.count ?? 0},
          }));
          if (ev.status === 'done') {
            this.loadProject(id); // refresh tab data live as each stage finishes
          }
        }
        break;
      case 'complete':
        this.analyzing.set(false);
        this.loadProject(id);
        break;
      case 'error':
        this.notifications.error(ev.message ?? 'Analysis error.');
        break;
    }
  }

  private loadProject(id: number) {
    this.projectService.getProjectById(id).subscribe({
      next: res => this.project.set(res.isSuccess ? res.data : null),
      error: () => this.project.set(null),
    });
  }

  catStatus(key: string): string {
    return this.progress()[key]?.status ?? '';
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
        if (!res.isSuccess) {
          this.analyzing.set(false);
          this.notifications.error(res.message);
          return;
        }
        this.notifications.success('Analysis started.');
      },
      error: () => {
        this.analyzing.set(false);
        this.notifications.error('Could not start analysis.');
      },
    });
  }

  scanPorts() {
    this.scanMenuOpen.set(false);
    const id = this.projectId();
    this.analyzing.set(true);
    this.activeTab.set('ports');
    this.projectService.scanPorts(id).subscribe({
      next: res => res.isSuccess
        ? this.notifications.success('Port scan started.')
        : this.notifications.error(res.message),
      error: () => this.notifications.error('Could not start port scan.'),
    });
  }

  scanPaths() {
    this.scanMenuOpen.set(false);
    const id = this.projectId();
    this.analyzing.set(true);
    this.activeTab.set('paths');
    this.projectService.scanPaths(id).subscribe({
      next: res => res.isSuccess
        ? this.notifications.success('Path scan started.')
        : this.notifications.error(res.message),
      error: () => this.notifications.error('Could not start path scan.'),
    });
  }

  toggleScanMenu() {
    this.scanMenuOpen.update(v => !v);
  }

  openNavLeft() {
    this.openNavLeftOutput.emit()
  }

  openNewProject() {
    this.openNewProjectOutput.emit()
  }
}
