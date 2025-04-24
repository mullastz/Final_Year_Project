import { TestBed } from '@angular/core/testing';

import { TransformRuleService } from './transform-rule.service';

describe('TransformRuleService', () => {
  let service: TransformRuleService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(TransformRuleService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
