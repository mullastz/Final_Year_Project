import { TestBed } from '@angular/core/testing';

import { ResourceUsageService } from './resource-usage.service';

describe('ResourceUsageService', () => {
  let service: ResourceUsageService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(ResourceUsageService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
