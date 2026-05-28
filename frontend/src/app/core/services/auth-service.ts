import {Injectable, inject, signal} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {ApiResponse} from '../model/ApiResponse';
import {config} from '../config';
import {of, tap} from 'rxjs';

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
    // return this.http.post<ApiResponse<{token: string}>>(`${config.apiUrl}/login`, {email, password}).pipe(tap(res => {
    //   localStorage.setItem("token", res.data.token)
    //   this.getMe().subscribe()
    // }));
    return of<ApiResponse<{token: string}>>({data:{token: "token"}, message: "test", isSuccess: true}).pipe(tap(res => {
      localStorage.setItem("token", res.data.token)
      this.getMe().subscribe()
    }));
  }

  register(email: string) {
    // return this.http.post<ApiResponse<null>>(`${config.apiUrl}/register`, {email})
    return of<ApiResponse<null>>({data:null, message: "test", isSuccess: true});
  }

  codeSubmit(email: string, code: string) {
    // return this.http.post<ApiResponse<{token: string}>>(`${config.apiUrl}/code/submit`, {email, code}).pipe(tap(res => {
    //   localStorage.setItem("token", res.data.token)
    //   this.getMe().subscribe()
    // }));
    return of<ApiResponse<{token: string}>>({data:{token: "token"}, message: "test", isSuccess: true}).pipe(tap(res => {
      localStorage.setItem("token", res.data.token)
      this.getMe().subscribe()
    }));
  }

  getMe() {
    // return this.http.get<ApiResponse<User>>(`${config.apiUrl}/me`).pipe(tap(res => {
    //   this._user.set(res.data);
    // }));
    return of<ApiResponse<User>>({data:{id: 1, email: "val.hvo@htlstp.at", created_at: "01.01.2000"}, message: "test", isSuccess: true}).pipe(tap(res => {
      this._user.set(res.data);
    }));
  }

  logout() {
    localStorage.removeItem("token");
    this._user.set(null);
  }
}
