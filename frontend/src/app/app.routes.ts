import { Routes } from '@angular/router';
import {Login} from './features/login/login';
export const routes: Routes = [
  {
    path: 'login',
    loadComponent: () => import('./features/login/login').then(m => m.Login),
    title: "Login"
  },
  {
    path: '**',
    loadComponent: () => import('./features/not-found-page/not-found-page').then(m => m.NotFoundPage),
    title: 'Page Not Found'
  }
];
