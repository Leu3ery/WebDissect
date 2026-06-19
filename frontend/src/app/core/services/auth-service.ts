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
    return this.http.post<ApiResponse<{token: string}>>(`${config.apiUrl}/auth/login`, {email, password}).pipe(tap(res => {
      if (res.isSuccess && res.data) {
        localStorage.setItem("token", res.data.token)
        this.getMe().subscribe()
      }
    }));
  }

  register(email: string) {
    return this.http.post<ApiResponse<null>>(`${config.apiUrl}/auth/register`, {email})
  }

  codeSubmit(email: string, code: string) {
    return this.http.post<ApiResponse<{token: string}>>(`${config.apiUrl}/auth/code/submit`, {email, code}).pipe(tap(res => {
      if (res.isSuccess && res.data) {
        localStorage.setItem("token", res.data.token)
        this.getMe().subscribe()
      }
    }));
  }

  getMe() {
    return this.http.get<ApiResponse<User>>(`${config.apiUrl}/auth/me`).pipe(tap(res => {
      if (res.isSuccess) {
        this._user.set(res.data);
      }
    }));
  }

  changePassword(password: string) {
    return this.http.patch<ApiResponse<null>>(`${config.apiUrl}/auth/me`, {password});
  }

  logout() {
    localStorage.removeItem("token");
    this._user.set(null);
  }
}
