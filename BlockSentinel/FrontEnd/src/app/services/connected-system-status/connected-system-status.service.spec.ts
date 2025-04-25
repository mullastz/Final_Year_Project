import { TestBed } from '@angular/core/testing';

import { ConnectedSystemStatusService } from './connected-system-status.service';

describe('ConnectedSystemStatusService', () => {
  let service: ConnectedSystemStatusService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(ConnectedSystemStatusService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
