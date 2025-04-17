import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SystemSyncComponent } from './system-sync.component';

describe('SystemSyncComponent', () => {
  let component: SystemSyncComponent;
  let fixture: ComponentFixture<SystemSyncComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SystemSyncComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(SystemSyncComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
