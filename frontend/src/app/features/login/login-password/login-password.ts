import {Component, computed, inject, signal} from '@angular/core';
import {FormBuilder, ReactiveFormsModule, Validators} from '@angular/forms';
import {JsonPipe} from '@angular/common';
import {toSignal} from '@angular/core/rxjs-interop';
import {AuthService} from '../../../core/services/auth-service';
import {Router} from '@angular/router';
import {merge} from 'rxjs';

@Component({
  selector: 'app-login-password',
  imports: [
    ReactiveFormsModule
  ],
  templateUrl: './login-password.html',
  styleUrl: './login-password.css',
})
export class LoginPassword {
  private fb = inject(FormBuilder);
  private authService = inject(AuthService);
  private router = inject(Router);
  error = signal('')
  form = this.fb.group({
    email: ['', [Validators.required, Validators.email, Validators.pattern("[a-z]+.[a-z]+@htlstp.at")]],
    password: ['', [Validators.required, Validators.minLength(8)]],
  })

  submit() {
    if (this.form.invalid) return;
    this.authService.login(this.form.controls.email.value!, this.form.controls.password.value!).subscribe(
      (res) => {
        if (!res.isSuccess) {
          this.error.set(res.message);
          return;
        }
        this.router.navigate(['/projects']);
      }
    )
  }
}
