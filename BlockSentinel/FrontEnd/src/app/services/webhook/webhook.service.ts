import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Webhook } from '../../interface/webhook';

@Injectable({
  providedIn: 'root'
})
export class WebhookService {
  private apiUrl = 'http://localhost:3011/webhooks';

  constructor(private http: HttpClient) {}

  getWebhooks(): Observable<Webhook[]> {
    return this.http.get<Webhook[]>(this.apiUrl);
  }

  addWebhook(webhook: Webhook): Observable<Webhook> {
    return this.http.post<Webhook>(this.apiUrl, webhook);
  }

  updateWebhook(id: number, webhook: Webhook): Observable<Webhook> {
    return this.http.put<Webhook>(`${this.apiUrl}/${id}`, webhook);
  }

  deleteWebhook(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${id}`);
  }
}
