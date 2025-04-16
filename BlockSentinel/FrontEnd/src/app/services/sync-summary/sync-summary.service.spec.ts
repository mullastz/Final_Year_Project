import { TestBed } from '@angular/core/testing';

import { SyncSummaryService } from './sync-summary.service';

describe('SyncSummaryService', () => {
  let service: SyncSummaryService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(SyncSummaryService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
