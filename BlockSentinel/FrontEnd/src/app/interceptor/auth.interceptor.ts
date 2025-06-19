import { Injectable } from '@angular/core';
import { HttpEvent, HttpInterceptor, HttpHandler, HttpRequest, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError, switchMap, catchError } from 'rxjs';
import { Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';

@Injectable()
export class AuthInterceptor implements HttpInterceptor {
  constructor(private http: HttpClient, private router: Router) {}

  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    // List of auth-related routes where we shouldn't attach tokens
    const skipAuthUrls = [
      'auth/login/',
      'auth/verify/',
      'auth/token/refresh/'
    ];
  
    const shouldSkip = skipAuthUrls.some(url => req.url.includes(url));
  
    let authReq = req;
  
    // ✅ Attach token only if it's not a login or OTP route
    if (!shouldSkip) {
      const accessToken = localStorage.getItem('access_token');
      if (accessToken) {
        authReq = req.clone({
          headers: req.headers.set('Authorization', `Bearer ${accessToken}`)
        });
      }
    }
  
    return next.handle(authReq).pipe(
      catchError((error: HttpErrorResponse) => {
        if ((error.status === 401 || error.status === 403) && !shouldSkip) {
          const refreshToken = localStorage.getItem('refresh_token');
          if (refreshToken) {
            return this.http.post<any>('http://127.0.0.1:8000/auth/token/refresh/', {
              refresh: refreshToken
            }).pipe(
              switchMap(response => {
                localStorage.setItem('access_token', response.access);
                const newReq = req.clone({
                  headers: req.headers.set('Authorization', `Bearer ${response.access}`)
                });
                return next.handle(newReq);
              }),
              catchError(refreshError => {
                this.router.navigate(['/']);
                return throwError(() => refreshError);
              })
            );
          } else {
            this.router.navigate(['/']);
          }
        }
  
        return throwError(() => error);
      })
    );
  }
}  
