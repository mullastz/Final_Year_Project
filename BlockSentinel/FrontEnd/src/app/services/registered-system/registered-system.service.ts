import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { map, Observable } from 'rxjs';
import { RegisteredSystem } from '../../interface/registered-system';

@Injectable({
  providedIn: 'root'
})
export class SystemService {
  private apiUrl = 'http://localhost:3000/systems';

  constructor(private http: HttpClient) {}

  getRegisteredSystems(): Observable<RegisteredSystem[]> {
    return this.http.get<RegisteredSystem[]>(this.apiUrl);
  }

  getSystemById(id: string): Observable<RegisteredSystem> {
    return this.http.get<RegisteredSystem[]>(this.apiUrl).pipe(
      map((systems: any[]) => systems.find((RegisteredSystem: { id: string; }) => RegisteredSystem.id === id)!)
    );
  }
  
}
