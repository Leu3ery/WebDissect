import {Component, computed, inject} from '@angular/core';
import {FormBuilder, ReactiveFormsModule, Validators} from '@angular/forms';
import {JsonPipe} from '@angular/common';
import {toSignal} from '@angular/core/rxjs-interop';

@Component({
  selector: 'app-login-password',
  imports: [
    ReactiveFormsModule,
    JsonPipe
  ],
  templateUrl: './login-password.html',
  styleUrl: './login-password.css',
})
export class LoginPassword {
  private fb = inject(FormBuilder);
  form = this.fb.group({
    email: ['', [Validators.required, Validators.email, Validators.pattern("[a-z]+.[a-z]+@htlstp.at")]],
    password: ['', [Validators.required, Validators.minLength(8)]],
  })

  private formStatus = toSignal(this.form.valueChanges);

  formError = computed(() => {
    this.formStatus(); // trigger recompute on change

    const { email, password } = this.form.controls;

    if (email.touched) {
      if (email.hasError('required'))  return 'Email is required';
      if (email.hasError('pattern'))   return 'Use your school email (firstname.lastname@htlstp.at)';
    }

    if (password.touched) {
      if (password.hasError('required'))    return 'Password is required';
      if (password.hasError('minlength'))   return 'Password must be at least 8 characters';
    }

    return null;
  });

  submit() {
    if (this.form.invalid) return;
  }
}
