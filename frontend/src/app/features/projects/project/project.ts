import {Component, computed, DestroyRef, effect, inject, input, numberAttribute, output, signal, untracked} from '@angular/core';
import {Router} from '@angular/router';
import {Observable, Subscription, switchMap, take, takeWhile, timer} from 'rxjs';
import {CertificateI, DnsEntryI, EndpointI, ProjectsService, TechnologyI} from '../projects-service';
import {LucideActivity, LucideGlobe, LucideLayers, LucideMenu, LucidePlay, LucideSearch, LucideShieldCheck, LucideTrash2, LucideUpload} from '@lucide/angular';
import {NotificationService} from '../../../schared/notifications/notification-service';
import {DnsTab} from './tabs/dns-tab/dns-tab';
import {TechTab} from './tabs/tech-tab/tech-tab';
import {EndpointsTab} from './tabs/endpoints-tab/endpoints-tab';
import {SslTab} from './tabs/ssl-tab/ssl-tab';

type TabId = 'dns' | 'tech' | 'ep' | 'ssl';

// Analysis runs in the background, so a tab can come up empty right after the
// page loads or an analysis is started. Re-fetch on an interval until data
// shows up, then stop. Bounded so we don't poll forever on genuinely empty data.
const POLL_INTERVAL_MS = 2500;
const MAX_POLL_ATTEMPTS = 30; // ~75s

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
    LucideTrash2,
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
  router = inject(Router)
  private destroyRef = inject(DestroyRef)

  uploading = signal(false)
  analyzing = signal(false)
  confirmingDelete = signal(false)
  deleting = signal(false)
  activeTab = signal<TabId>('dns')

  // Base project info comes from the shared projects list — no extra request.
  project = computed(() =>
    this.projectService.projects().find(p => p.id === this.projectId()) ?? null
  )
  // Distinguish "still loading the list" from a genuinely missing project.
  notFound = computed(() =>
    this.projectService.projectsLoaded() && this.project() === null
  )

  // Per-tab data, fetched lazily the first time a tab is opened.
  dnsEntries = signal<DnsEntryI[]>([])
  certificates = signal<CertificateI[]>([])
  endpoints = signal<EndpointI[]>([])
  technologies = signal<TechnologyI[]>([])

  loading = signal<Record<TabId, boolean>>({dns: false, tech: false, ep: false, ssl: false})
  errors = signal<Record<TabId, string>>({dns: '', tech: '', ep: '', ssl: ''})

  // Analysis id each tab's data was loaded for, so we only re-fetch when the
  // project (or its latest analysis) actually changes.
  private loadedKey: Record<TabId, string | null> = {dns: null, tech: null, ep: null, ssl: null}
  private currentProjectId: number | null = null
  // Active long-poll subscription per tab, so we can cancel/replace it.
  private pollSubs: Record<TabId, Subscription | null> = {dns: null, tech: null, ep: null, ssl: null}

  constructor() {
    this.destroyRef.onDestroy(() => this.stopAllPolling());
    effect(() => {
      const proj = this.project();
      const tab = this.activeTab();
      untracked(() => {
        if (!proj) {
          return;
        }
        if (proj.id !== this.currentProjectId) {
          this.resetTabs(proj.id);
        }
        this.ensureTab(tab, proj.analysisId);
      });
    });
  }

  private resetTabs(projectId: number) {
    this.currentProjectId = projectId;
    this.confirmingDelete.set(false);
    this.stopAllPolling();
    this.loadedKey = {dns: null, tech: null, ep: null, ssl: null};
    this.dnsEntries.set([]);
    this.certificates.set([]);
    this.endpoints.set([]);
    this.technologies.set([]);
    this.errors.set({dns: '', tech: '', ep: '', ssl: ''});
  }

  // Fetch the active tab's data unless it is already loaded for this analysis.
  private ensureTab(tab: TabId, analysisId: number | null) {
    const key = `${analysisId}`;
    if (this.loadedKey[tab] === key) {
      return;
    }

    // The three real tabs need an analysis to query; without one there is
    // nothing to show. The tech tab is mocked, so it loads regardless.
    if (tab !== 'tech' && analysisId === null) {
      this.loadedKey[tab] = key;
      return;
    }

    this.loadedKey[tab] = key;

    switch (tab) {
      case 'dns':
        this.poll(tab,
          this.projectService.getDnsEntries(analysisId!),
          data => (data ?? []).length === 0,
          data => this.dnsEntries.set(data ?? []),
          'Could not load DNS records.');
        break;
      case 'ssl':
        this.poll(tab,
          this.projectService.getCertificate(analysisId!),
          cert => !cert,
          cert => this.certificates.set(cert ? [cert] : []),
          'Could not load TLS certificate.');
        break;
      case 'ep':
        this.poll(tab,
          this.projectService.getEndpoints(analysisId!),
          data => (data ?? []).length === 0,
          data => this.endpoints.set(data ?? []),
          'Could not load endpoints.');
        break;
      case 'tech':
        this.poll(tab,
          this.projectService.getTechnologies(analysisId ?? 0),
          data => (data ?? []).length === 0,
          data => this.technologies.set(data ?? []),
          'Could not load technologies.');
        break;
    }
  }

  // Long-poll `fetch$` until `isEmpty` is false (data arrived) or attempts run
  // out, applying every response so the UI fills in as soon as it's ready.
  private poll<T>(
    tab: TabId,
    fetch$: Observable<T>,
    isEmpty: (data: T) => boolean,
    apply: (data: T) => void,
    errMsg: string,
  ) {
    this.pollSubs[tab]?.unsubscribe();
    this.setLoading(tab, true);
    this.setError(tab, '');

    let lastEmpty = true;
    this.pollSubs[tab] = timer(0, POLL_INTERVAL_MS).pipe(
      take(MAX_POLL_ATTEMPTS),
      switchMap(() => fetch$),
      // Keep going while empty; emit the first non-empty response, then stop.
      takeWhile(data => isEmpty(data), true),
    ).subscribe({
      next: data => {
        lastEmpty = isEmpty(data);
        apply(data);
        if (!lastEmpty) {
          this.setLoading(tab, false);
        }
      },
      error: () => {
        this.loadedKey[tab] = null; // allow a retry on the next visit
        this.setLoading(tab, false);
        this.setError(tab, errMsg);
      },
      complete: () => {
        this.setLoading(tab, false);
        // Gave up while still empty — let a re-visit start a fresh poll.
        if (lastEmpty) {
          this.loadedKey[tab] = null;
        }
      },
    });
  }

  private stopAllPolling() {
    (Object.keys(this.pollSubs) as TabId[]).forEach(tab => {
      this.pollSubs[tab]?.unsubscribe();
      this.pollSubs[tab] = null;
    });
  }

  private setLoading(tab: TabId, value: boolean) {
    this.loading.update(s => ({...s, [tab]: value}));
  }

  private setError(tab: TabId, value: string) {
    this.errors.update(s => ({...s, [tab]: value}));
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
          this.notifications.error(res.errorMessage ?? 'Could not upload HAR file.');
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
          this.notifications.error(res.errorMessage ?? 'Could not start analysis.');
          return;
        }
        this.notifications.success('Analysis started.');
        // Refresh the list so the project picks up its new latest analysis id;
        // the effect then re-fetches the active tab against it.
        this.projectService.getProjects().subscribe();
      },
      error: () => {
        this.analyzing.set(false);
        this.notifications.error('Could not start analysis.');
      },
    });
  }

  requestDelete() {
    this.confirmingDelete.set(true);
  }

  cancelDelete() {
    this.confirmingDelete.set(false);
  }

  confirmDelete() {
    if (this.deleting()) {
      return;
    }
    const id = this.projectId();
    this.deleting.set(true);
    this.projectService.deleteProject(id).subscribe({
      next: res => {
        this.deleting.set(false);
        this.confirmingDelete.set(false);
        if (!res.isSuccess) {
          this.notifications.error(res.errorMessage ?? 'Could not delete project.');
          return;
        }
        this.notifications.success('Project deleted.');
        this.router.navigate(['/projects']);
      },
      error: () => {
        this.deleting.set(false);
        this.notifications.error('Could not delete project.');
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
