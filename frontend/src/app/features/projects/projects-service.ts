import {inject, Injectable, signal} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {ApiResponse} from '../../core/model/ApiResponse';
import {config} from '../../core/config';
import {Observable, of, tap} from 'rxjs';

export interface ProjectI {
  id: number;
  name: string;
  domain: string;
}

export interface ProjectCreateI {
  name: string;
  domain: string;
  har?: File;
}

@Injectable({
  providedIn: 'root',
})
export class ProjectsService {
  private http = inject(HttpClient);
  private _projects = signal<ProjectI[]>([])
  readonly projects = this._projects.asReadonly()

  getProjects() {
    // return this.http.get<ApiResponse<Project[]>>(`${config.apiUrl}/projects`).pipe(tap(res => {
    //   this._projects.set(res.data)
    // }));
    return of<ApiResponse<ProjectI[]>>({data:[{id: 1, name: "project 1", domain: "test.com"}, {id: 2, name: "project 2", domain: "webdissect.online"}], message: "test", isSuccess: true}).pipe(tap(res => {
        this._projects.set(res.data)
      }));
  }

  getProjectById(id: number): Observable<ApiResponse<ProjectI>> {
    // return this.http.get<ApiResponse<ProjectI>>(`${config.apiUrl}/projects/${id}`)
    if (id >= 3) {
      return of<ApiResponse<ProjectI>>({data:{id: 2, name: "project 1", domain: "test.com"}, message: "test", isSuccess: false})
    }
    return of<ApiResponse<ProjectI>>({data:{id: 2, name: "project 1", domain: "test.com"}, message: "test", isSuccess: true})
  }


  createProject(project: ProjectCreateI) {
    // const formData = new FormData();
    // formData.append('name', project.name);
    // formData.append('domain', project.domain);
    // if (project.har) {
    //   formData.append('har', project.har);
    // }
    // return this.http.post<ApiResponse<Project>>(`${config.apiUrl}/projects`, formData)
    return of<ApiResponse<ProjectI>>({data:{id: 2, name: "project 1", domain: "test.com"}, message: "test", isSuccess: true})
  }
}
