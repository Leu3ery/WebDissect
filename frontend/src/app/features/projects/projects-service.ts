import {inject, Injectable, signal} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {ApiResponse} from '../../core/model/ApiResponse';
import {config} from '../../core/config';
import {delay, map, Observable, of, switchMap, tap} from 'rxjs';

export interface ProjectI {
  id: number;
  name: string;
  domain: string;
  // Latest analysis id (null until the first analysis has been started).
  analysisId: number | null;
}

// Raw shape returned by GET /api/projects: each item wraps the base project
// info together with the id of its latest analysis.
interface ProjectWithAnalysisIdI {
  project: {
    id: number;
    name: string;
    domain: string;
  };
  analysis_id: number | null;
}

export interface CertificateI {
  id: number;
  subject_domain: string;
  subject_organization: string;
  subject_country: string;
  issuer_name: string;
  issuer_organization: string;
  issuer_country: string;
  valid_from: string;
  valid_to: string;
  serial_number: string;
  public_key_type: string;
  fingerprint_sha256: string;
}

export interface DnsEntryI {
  id: number;
  type: string;
  domain: string;
  value: string;
  ttl: number;
}

export interface TechnologyI {
  id: number;
  name: string;
  description: string;
  icon_url: string;
}

export interface EndpointI {
  id: number;
  method: string;
  path: string;
  status: number;
  content_type: string;
}

export interface ProjectCreateI {
  name: string;
  domain: string;
}

export interface CreateProjectResultI {
  projectId: number;
}

export interface ProjectUpdateI {
  name?: string;
  domain?: string;
}

@Injectable({
  providedIn: 'root',
})
export class ProjectsService {
  private http = inject(HttpClient);
  private _projects = signal<ProjectI[]>([])
  readonly projects = this._projects.asReadonly()
  private _projectsLoaded = signal(false)
  // True once the projects list has been fetched at least once — lets the UI
  // tell "still loading" apart from "project not found".
  readonly projectsLoaded = this._projectsLoaded.asReadonly()

  // Loads the list of projects (base info + latest analysis id). This is the
  // single source of truth for the per-project header shown in the UI; the
  // individual tabs fetch their own data lazily via the methods below.
  getProjects(): Observable<ApiResponse<ProjectWithAnalysisIdI[]>> {
    return this.http.get<ApiResponse<ProjectWithAnalysisIdI[]>>(`${config.apiUrl}/projects`).pipe(
      tap(res => {
        if (res.isSuccess && res.data) {
          this._projects.set(res.data.map(item => ({
            id: item.project.id,
            name: item.project.name,
            domain: item.project.domain,
            analysisId: item.analysis_id,
          })));
        }
        this._projectsLoaded.set(true);
      })
    );
  }

  // ~~~~~~~~~~ # Per-tab analysis data # ~~~~~~~~~~ #
  // Each tab is backed by a dedicated endpoint keyed on the analysis id.
  // These responses are raw (not wrapped in ApiResponse).

  getDnsEntries(analysisId: number): Observable<DnsEntryI[]> {
    return this.http.get<DnsEntryI[]>(`${config.apiUrl}/dns/${analysisId}`);
  }

  getCertificate(analysisId: number): Observable<CertificateI | null> {
    return this.http.get<CertificateI | null>(`${config.apiUrl}/tls/${analysisId}`);
  }

  getEndpoints(analysisId: number): Observable<EndpointI[]> {
    return this.http.get<EndpointI[]>(`${config.apiUrl}/har/${analysisId}`);
  }

  // No backend endpoint for tech detection yet — return mock data for now.
  getTechnologies(_analysisId: number): Observable<TechnologyI[]> {
    return of<TechnologyI[]>([
      {id: 1, name: "Nginx", description: "Web server", icon_url: "https://icon.icepanel.io/Technology/svg/NGINX.svg"},
      {id: 2, name: "React", description: "Frontend library", icon_url: "https://icon.icepanel.io/Technology/svg/React.svg"},
      {id: 3, name: "Cloudflare", description: "CDN / WAF", icon_url: "https://icon.icepanel.io/Technology/svg/Cloudflare.svg"},
    ]).pipe(delay(300));
  }

  createProject(project: ProjectCreateI): Observable<ApiResponse<CreateProjectResultI>> {
    return this.http.post<ApiResponse<CreateProjectResultI>>(`${config.apiUrl}/projects`, project);
  }

  uploadHar(id: number, har: File): Observable<ApiResponse<null>> {
    const formData = new FormData();
    formData.append('file', har);
    return this.http.post<ApiResponse<null>>(`${config.apiUrl}/projects/${id}/upload`, formData);
    // return of<ApiResponse<null>>({data: null, message: "test", isSuccess: true}).pipe(delay(400))
  }

  updateProject(id: number, project: ProjectUpdateI): Observable<ApiResponse<null>> {
    return this.http.patch<ApiResponse<null>>(`${config.apiUrl}/projects/${id}`, project);
  }

  startAnalysis(id: number): Observable<ApiResponse<null>> {
    return this.http.post<ApiResponse<null>>(`${config.apiUrl}/projects/${id}/analysis/start`, {});
  }

  deleteProject(id: number): Observable<ApiResponse<null>> {
    return this.http.delete<ApiResponse<null>>(`${config.apiUrl}/projects/${id}`).pipe(
      tap(res => {
        if (res.isSuccess) {
          // Drop it from the shared list immediately so the UI updates.
          this._projects.set(this._projects().filter(p => p.id !== id));
        }
      })
    );
  }

  // Creating a project is a 3-step flow: create the project, upload the HAR
  // file (if provided) and finally start the analysis. Returns the created
  // project's id, or the first failing step's response.
  createProjectWithAnalysis(project: ProjectCreateI, har?: File | null): Observable<ApiResponse<CreateProjectResultI>> {
    return this.createProject(project).pipe(
      switchMap(createRes => {
        if (!createRes.isSuccess) {
          return of(createRes);
        }
        const id = createRes.data.projectId;
        const upload$ = har
          ? this.uploadHar(id, har)
          : of<ApiResponse<null>>({data: null, isSuccess: true});

        return upload$.pipe(
          switchMap(uploadRes => {
            if (!uploadRes.isSuccess) {
              return of<ApiResponse<CreateProjectResultI>>({...createRes, isSuccess: false, errorMessage: uploadRes.errorMessage});
            }
            return this.startAnalysis(id).pipe(
              map(startRes => startRes.isSuccess
                ? createRes
                : {...createRes, isSuccess: false, errorMessage: startRes.errorMessage}),
            );
          }),
        );
      }),
    );
  }
}
