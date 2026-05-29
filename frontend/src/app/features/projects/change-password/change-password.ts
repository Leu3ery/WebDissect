import {Component, inject, output, signal} from '@angular/core';
import {LucideKey} from '@lucide/angular';
import {AbstractControl, FormBuilder, ReactiveFormsModule, Validators} from '@angular/forms';
import {JsonPipe} from '@angular/common';
import {AuthService} from '../../../core/services/auth-service';

@Component({
  selector: 'app-change-password',
  imports: [
    LucideKey,
    ReactiveFormsModule,
    JsonPipe
  ],
  templateUrl: './change-password.html',
  styleUrl: './change-password.css',
})
export class ChangePassword {
  backFromChangePassword = output()
  closeChangePassword = output()
  authService = inject(AuthService)
  private fb = inject(FormBuilder)
  error = signal('')
  form = this.fb.group({
    password1: ['', [Validators.required, Validators.minLength(8)]],
    password2: ['', [Validators.required, Validators.minLength(8)]],
  }, {
    validators: [this.arePasswordsSame]
  })

  ngOnInit() {
    this.form.valueChanges.subscribe(change => {
      if (this.error()) {
        this.error.set('')
      }
    })
  }

  arePasswordsSame(control: AbstractControl) {
    const p1 = control.get('password1');
    const p2 = control.get('password2');
    return p1?.value === p2?.value ? null : { passwordsMismatch: true };
  }

  submit() {
    this.authService.changePassword(this.form.controls.password1.value!).subscribe(res => {
      if (!res.isSuccess) {
        this.error.set(res.message)
      } else {
        this.closeChangePassword.emit()
      }
    })
  }
}
