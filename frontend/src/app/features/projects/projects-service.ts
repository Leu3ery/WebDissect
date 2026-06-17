import {inject, Injectable, signal} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {ApiResponse} from '../../core/model/ApiResponse';
import {config} from '../../core/config';
import {delay, map, Observable, of, switchMap, tap} from 'rxjs';

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

export interface ProjectFullI extends ProjectI {
  certificates: CertificateI[];
  dns_entries: DnsEntryI[];
  technologies: TechnologyI[];
  endpoints: EndpointI[];
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

  getProjects(): Observable<ApiResponse<{projects: ProjectI[]}>> {
    return this.http.get<ApiResponse<{projects: ProjectI[]}>>(`${config.apiUrl}/projects`).pipe(
      tap(res => {
        if (res.isSuccess) {
          this._projects.set(res.data.projects)
        }
      })
    );
    // return of<ApiResponse<ProjectI[]>>({
    //   data: [
    //     {id: 1, name: "project 1", domain: "test.com", user_id: 1},
    //     {id: 2, name: "project 2", domain: "webdissect.online", user_id: 1},
    //   ],
    //   message: "test",
    //   isSuccess: true,
    // }).pipe(delay(400), tap(res => {
    //   if (res.isSuccess) {
    //     this._projects.set(res.data)
    //   }
    // }));
  }

  getProjectById(id: number): Observable<ApiResponse<ProjectFullI>> {
    // return this.http.get<ApiResponse<ProjectFullI>>(`${config.apiUrl}/projects/${id}`);
    if (id >= 3) {
      return of<ApiResponse<ProjectFullI>>({
        data: null as unknown as ProjectFullI,
        message: "Project not found",
        isSuccess: false,
      }).pipe(delay(400))
    }
    return of<ApiResponse<ProjectFullI>>({
      data: {
        id,
        name: "project 1",
        domain: "test.com",
        user_id: 1,
        certificates: [
          {
            id: 1,
            subject_domain: "test.com",
            subject_organization: "Test Inc.",
            subject_country: "US",
            issuer_name: "R3",
            issuer_organization: "Let's Encrypt",
            issuer_country: "US",
            valid_from: "2026-01-01T00:00:00Z",
            valid_to: "2026-04-01T00:00:00Z",
            serial_number: "03:AB:CD:EF:12:34:56:78",
            public_key_type: "RSA",
            fingerprint_sha256: "a1b2c3d4e5f60718293a4b5c6d7e8f90a1b2c3d4e5f60718293a4b5c6d7e8f90",
          },
        ],
        dns_entries: [
          {id: 1, type: "A", domain: "test.com", value: "93.184.216.34", ttl: 3600},
          {id: 2, type: "AAAA", domain: "test.com", value: "2606:2800:220:1:248:1893:25c8:1946", ttl: 3600},
          {id: 3, type: "MX", domain: "test.com", value: "mail.test.com", ttl: 7200},
          {id: 4, type: "TXT", domain: "test.com", value: "v=spf1 include:_spf.test.com ~all", ttl: 3600},
        ],
        technologies: [
          {id: 1, name: "Nginx", description: "Web server", icon_url: "https://icon.icepanel.io/Technology/svg/NGINX.svg"},
          {id: 2, name: "React", description: "Frontend library", icon_url: "https://icon.icepanel.io/Technology/svg/React.svg"},
          {id: 3, name: "Cloudflare", description: "CDN / WAF", icon_url: "https://icon.icepanel.io/Technology/svg/Cloudflare.svg"},
        ],
        endpoints: [
          {id: 1, method: "GET", path: "/", status: 200, content_type: "text/html"},
          {id: 2, method: "GET", path: "/api/users", status: 200, content_type: "application/json"},
          {id: 3, method: "POST", path: "/api/auth/login", status: 401, content_type: "application/json"},
          {id: 4, method: "DELETE", path: "/api/users/5", status: 204, content_type: "application/json"},
        ],
      },
      message: "test",
      isSuccess: true,
    }).pipe(delay(400))
  }

  createProject(project: ProjectCreateI): Observable<ApiResponse<ProjectI>> {
    return this.http.post<ApiResponse<ProjectI>>(`${config.apiUrl}/projects`, project);
    // return of<ApiResponse<ProjectI>>({
    //   data: {id: 2, name: project.name, domain: project.domain, user_id: 1},
    //   message: "test",
    //   isSuccess: true,
    // }).pipe(delay(400))
  }

  uploadHar(id: number, har: File): Observable<ApiResponse<null>> {
    const formData = new FormData();
    formData.append('file', har);
    return this.http.post<ApiResponse<null>>(`${config.apiUrl}/projects/${id}/upload`, formData);
    // return of<ApiResponse<null>>({data: null, message: "test", isSuccess: true}).pipe(delay(400))
  }

  updateProject(id: number, project: ProjectUpdateI): Observable<ApiResponse<ProjectI>> {
    // return this.http.patch<ApiResponse<ProjectI>>(`${config.apiUrl}/projects/${id}`, project);
    return of<ApiResponse<ProjectI>>({
      data: {id, name: project.name ?? "project 1", domain: project.domain ?? "test.com", user_id: 1},
      message: "test",
      isSuccess: true,
    }).pipe(delay(400))
  }

  startAnalysis(id: number): Observable<ApiResponse<null>> {
    return this.http.post<ApiResponse<null>>(`${config.apiUrl}/projects/${id}/analysis/start`, {});
    // return of<ApiResponse<null>>({data: null, message: "test", isSuccess: true}).pipe(delay(400))
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
