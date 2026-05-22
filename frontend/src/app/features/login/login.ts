import {Component, signal} from '@angular/core';
import {LoginPassword} from './login-password/login-password';
import {LoginEmail} from './login-email/login-email';

@Component({
  selector: 'app-login',
  imports: [
    LoginPassword,
    LoginEmail
  ],
  templateUrl: './login.html',
  styleUrl: './login.css',
})
export class Login {
  isLoginWithPassword = signal(false);

  toggleLoginPage() {
    this.isLoginWithPassword.set(!this.isLoginWithPassword())
  }
}
