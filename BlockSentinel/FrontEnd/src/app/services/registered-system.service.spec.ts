import { TestBed } from '@angular/core/testing';

import { RegisteredSystemService } from './registered-system.service';

describe('RegisteredSystemService', () => {
  let service: RegisteredSystemService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(RegisteredSystemService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
