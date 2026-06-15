import {inject, Injectable, signal} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {ApiResponse} from '../../core/model/ApiResponse';
import {config} from '../../core/config';
import {map, Observable, of, switchMap, tap} from 'rxjs';

export interface ProjectI {
  id: number;
  name: string;
  domain: string;
  user_id: number;
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

export interface SubdomainI {
  id: number;
  name: string;
  ip: string;
  source: string;
}

export interface PortI {
  id: number;
  port: number;
  protocol: string;
  state: string;
  service: string;
  version: string;
  banner: string;
}

export interface PathEntryI {
  id: number;
  path: string;
  status: number;
  content_type: string;
  length: number;
}

export interface SecurityCheckI {
  id: number;
  category: string;
  name: string;
  status: string;
  severity: string;
  detail: string;
}

export interface AnalysisRunI {
  id: number;
  created_at: string;
  kind: string;
  counts: Record<string, number>;
}

export interface ProjectFullI extends ProjectI {
  certificates: CertificateI[];
  dns_entries: DnsEntryI[];
  technologies: TechnologyI[];
  endpoints: EndpointI[];
  subdomains: SubdomainI[];
  ports: PortI[];
  path_entries: PathEntryI[];
  security_checks: SecurityCheckI[];
}

export interface ProjectCreateI {
  name: string;
  domain: string;
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

  getProjects(): Observable<ApiResponse<ProjectI[]>> {
    return this.http.get<ApiResponse<ProjectI[]>>(`${config.apiUrl}/projects`).pipe(
      tap(res => {
        if (res.isSuccess) {
          this._projects.set(res.data)
        }
      })
    );
  }

  getProjectById(id: number): Observable<ApiResponse<ProjectFullI>> {
    return this.http.get<ApiResponse<ProjectFullI>>(`${config.apiUrl}/projects/${id}`);
  }

  createProject(project: ProjectCreateI): Observable<ApiResponse<ProjectI>> {
    return this.http.post<ApiResponse<ProjectI>>(`${config.apiUrl}/projects`, project);
  }

  uploadHar(id: number, har: File): Observable<ApiResponse<null>> {
    const formData = new FormData();
    formData.append('file', har);
    return this.http.post<ApiResponse<null>>(`${config.apiUrl}/projects/${id}/upload`, formData);
  }

  updateProject(id: number, project: ProjectUpdateI): Observable<ApiResponse<ProjectI>> {
    return this.http.patch<ApiResponse<ProjectI>>(`${config.apiUrl}/projects/${id}`, project);
  }

  startAnalysis(id: number): Observable<ApiResponse<null>> {
    return this.http.post<ApiResponse<null>>(`${config.apiUrl}/projects/${id}/analysis/start`, {});
  }

  scanPorts(id: number): Observable<ApiResponse<null>> {
    return this.http.post<ApiResponse<null>>(`${config.apiUrl}/projects/${id}/scan/ports`, {});
  }

  scanPaths(id: number): Observable<ApiResponse<null>> {
    return this.http.post<ApiResponse<null>>(`${config.apiUrl}/projects/${id}/scan/paths`, {});
  }

  getHistory(id: number): Observable<ApiResponse<AnalysisRunI[]>> {
    return this.http.get<ApiResponse<AnalysisRunI[]>>(`${config.apiUrl}/projects/${id}/history`);
  }

  exportJson(id: number): Observable<Blob> {
    return this.http.get(`${config.apiUrl}/projects/${id}/export/json`, {responseType: 'blob'});
  }

  exportPdf(id: number): Observable<Blob> {
    return this.http.get(`${config.apiUrl}/projects/${id}/export/pdf`, {responseType: 'blob'});
  }

  // Creating a project is a 3-step flow: create the project, upload the HAR
  // file (if provided) and finally start the analysis. Returns the created
  // project, or the first failing step's response.
  createProjectWithAnalysis(project: ProjectCreateI, har?: File | null): Observable<ApiResponse<ProjectI>> {
    return this.createProject(project).pipe(
      switchMap(createRes => {
        if (!createRes.isSuccess) {
          return of(createRes);
        }
        const id = createRes.data.id;
        const upload$ = har
          ? this.uploadHar(id, har)
          : of<ApiResponse<null>>({data: null, message: "", isSuccess: true});

        return upload$.pipe(
          switchMap(uploadRes => {
            if (!uploadRes.isSuccess) {
              return of<ApiResponse<ProjectI>>({...createRes, isSuccess: false, message: uploadRes.message});
            }
            return this.startAnalysis(id).pipe(
              map(startRes => startRes.isSuccess
                ? createRes
                : {...createRes, isSuccess: false, message: startRes.message}),
            );
          }),
        );
      }),
    );
  }
}
