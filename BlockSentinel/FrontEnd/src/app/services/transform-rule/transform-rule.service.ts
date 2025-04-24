import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { TransformRule } from '../../interface/transform-rule';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class TransformRuleService {
  private apiUrl = 'http://localhost:3010/transformRules';

  constructor(private http: HttpClient) {}

  getAll(): Observable<TransformRule[]> {
    return this.http.get<TransformRule[]>(this.apiUrl);
  }

  update(id: string, data: Partial<TransformRule>): Observable<TransformRule> {
    return this.http.patch<TransformRule>(`${this.apiUrl}/${id}`, data);
  }

  delete(id: string): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${id}`);
  }
}
