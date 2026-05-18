import { ComponentFixture, TestBed } from '@angular/core/testing';

import { LoginEmail } from './login-email';

describe('LoginEmail', () => {
  let component: LoginEmail;
  let fixture: ComponentFixture<LoginEmail>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [LoginEmail]
    })
    .compileComponents();

    fixture = TestBed.createComponent(LoginEmail);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
