import { ComponentFixture, TestBed } from '@angular/core/testing';

import { LoginPassword } from './login-password';

describe('LoginPassword', () => {
  let component: LoginPassword;
  let fixture: ComponentFixture<LoginPassword>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [LoginPassword]
    })
    .compileComponents();

    fixture = TestBed.createComponent(LoginPassword);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
