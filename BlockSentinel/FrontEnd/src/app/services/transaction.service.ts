import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Transaction } from '../interface/transaction';

@Injectable({
  providedIn: 'root'
})
export class TransactionService {
  private apiUrl = 'http://127.0.0.1:8000/auditlog/transactions/';

  constructor(private http: HttpClient) {}

  getTransaction(): Observable<Transaction[]> {
    return this.http.get<Transaction[]>(this.apiUrl);
  }
  
  getAuditSummary(): Observable<any> {
    return this.http.get<any>('http://127.0.0.1:8000/auditlog/system-status/');
  }
  
}
