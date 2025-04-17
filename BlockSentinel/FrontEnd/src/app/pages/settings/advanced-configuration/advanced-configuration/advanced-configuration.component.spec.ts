import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AdvancedConfigurationComponent } from './advanced-configuration.component';

describe('AdvancedConfigurationComponent', () => {
  let component: AdvancedConfigurationComponent;
  let fixture: ComponentFixture<AdvancedConfigurationComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AdvancedConfigurationComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AdvancedConfigurationComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
