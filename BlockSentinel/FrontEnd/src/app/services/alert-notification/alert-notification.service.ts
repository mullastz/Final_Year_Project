import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { AlertNotification } from '../../interface/alerts-notification';

@Injectable({
  providedIn: 'root'
})
export class AlertNotificationService {
  private jsonUrl = 'http://localhost:3015/alerts-notification';

  constructor(private http: HttpClient) {}

  getAlerts(): Observable<AlertNotification[]> {
    return this.http.get<AlertNotification[]>(this.jsonUrl);
  }
}
