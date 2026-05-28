import {HttpHandlerFn, HttpRequest} from '@angular/common/http';
import {inject} from '@angular/core';
import {Router} from '@angular/router';
import {catchError, EMPTY} from 'rxjs';

export function authInterceptor(req: HttpRequest<unknown>, next: HttpHandlerFn) {
  if (toPassThrough(req.url)) {
    return next(req);
  }
  const router = inject(Router);
  const token = localStorage.getItem("token");
  if (!token) {
    router.navigate(['/login']);
    return EMPTY;
  }
  const newRequest = req.clone({
    headers: req.headers.set('Authorization', 'Bearer ' + token),
  })

  return next(newRequest).pipe(
    catchError(err => {
      if (err.status == 401) {
        router.navigate(['/login'])
        localStorage.removeItem("token")
        return EMPTY;
      }
      throw err;
    })
  );
}

function toPassThrough(url: string) {
  return (
    url.includes("/login") ||
    url.includes("/register") ||
    url.includes("/code/submit")
  )
}
