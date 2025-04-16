import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { map, Observable } from 'rxjs';
import { Ledger } from '../../interface/ledger';

@Injectable({ providedIn: 'root' })
export class LedgerService {
  constructor(private http: HttpClient) {}

  getLedgerBySystemAndBatch(systemId: string, batchId: string): Observable<Ledger | undefined> {
    return this.http.get<Ledger[]>('http://localhost:3005/ledger').pipe(
      map((ledgers: any[]) => ledgers.find(ledger => ledger.systemId === systemId && ledger.batchId === batchId))
    );
  }
}
