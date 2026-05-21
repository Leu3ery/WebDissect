import {Injectable, inject, signal} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {ApiResponse} from '../model/ApiResponse';
import {config} from '../config';
import {tap} from 'rxjs';

export interface User {
  id: number;
  email: string;
  created_at: string;
}

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private http = inject(HttpClient);
  private _user= signal<User | null>(null);
  readonly user = this._user.asReadonly();

  login(email: string, password: string) {
    return this.http.post<ApiResponse<{token: string}>>(`${config.apiUrl}/login`, {email, password}).pipe(tap(res => {
      localStorage.setItem("token", res.data.token)
    }));
  }

  register(email: string) {
    return this.http.post<ApiResponse<null>>(`${config.apiUrl}/register`, {email})
  }

  codeSubmit(email: string, code: number) {
    return this.http.post<ApiResponse<{token: string}>>(`${config.apiUrl}/code/submit`, {email, code}).pipe(tap(res => {
      localStorage.setItem("token", res.data.token)
    }));
  }

  getMe() {
    return this.http.get<ApiResponse<User>>(`${config.apiUrl}/me`).pipe(tap(res => {
      this._user.set(res.data);
    }));
  }
}
