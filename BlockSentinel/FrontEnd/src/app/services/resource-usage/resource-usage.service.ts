import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { ResourceUsage } from '../../interface/resource-usage';

@Injectable({
  providedIn: 'root'
})
export class ResourceUsageService {
  private jsonUrl = 'http://localhost:3013/resource-usage';

  constructor(private http: HttpClient) {}

  getResourceUsage(): Observable<ResourceUsage[]> {
    return this.http.get<ResourceUsage[]>(this.jsonUrl);
  }
}
