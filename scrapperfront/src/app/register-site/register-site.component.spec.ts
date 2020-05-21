import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { RegisterSiteComponent } from './register-site.component';

describe('RegisterSiteComponent', () => {
  let component: RegisterSiteComponent;
  let fixture: ComponentFixture<RegisterSiteComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ RegisterSiteComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(RegisterSiteComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
