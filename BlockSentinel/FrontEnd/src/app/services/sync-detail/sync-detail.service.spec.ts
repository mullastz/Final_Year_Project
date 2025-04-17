import { TestBed } from '@angular/core/testing';

import { SyncDetailService } from './sync-detail.service';

describe('SyncDetailService', () => {
  let service: SyncDetailService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(SyncDetailService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
