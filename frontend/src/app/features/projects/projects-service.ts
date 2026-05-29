import {inject, Injectable, signal} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {ApiResponse} from '../../core/model/ApiResponse';
import {config} from '../../core/config';
import {of, tap} from 'rxjs';

export interface Project {
  id: number;
  name: string;
  domain: string;
}

@Injectable({
  providedIn: 'root',
})
export class ProjectsService {
  private http = inject(HttpClient);
  private _projects = signal<Project[]>([])
  readonly projects = this._projects.asReadonly()

  getProjects() {
    // return this.http.get<ApiResponse<Project[]>>(`${config.apiUrl}/projects`).pipe(tap(res => {
    //   this._projects.set(res.data)
    // }));
    return of<ApiResponse<Project[]>>({data:[{id: 1, name: "project 1", domain: "test.com"}, {id: 2, name: "project 2", domain: "webdissect.online"}], message: "test", isSuccess: true}).pipe(tap(res => {
        this._projects.set(res.data)
      }));
  }
}
