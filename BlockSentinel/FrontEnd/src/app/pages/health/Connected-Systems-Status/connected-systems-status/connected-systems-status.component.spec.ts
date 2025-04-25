import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ConnectedSystemsStatusComponent } from './connected-systems-status.component';

describe('ConnectedSystemsStatusComponent', () => {
  let component: ConnectedSystemsStatusComponent;
  let fixture: ComponentFixture<ConnectedSystemsStatusComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ConnectedSystemsStatusComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ConnectedSystemsStatusComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
