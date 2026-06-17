import {Component, ElementRef, inject, QueryList, signal, ViewChild, ViewChildren} from '@angular/core';
import {FormArray, FormBuilder, ReactiveFormsModule, Validators} from '@angular/forms';
import {AuthService} from '../../../core/services/auth-service';
import {Router} from '@angular/router';

@Component({
  selector: 'app-login-email',
  imports: [
    ReactiveFormsModule
  ],
  templateUrl: './login-email.html',
  styleUrl: './login-email.css',
})
export class LoginEmail {
  @ViewChildren('digitInput') inputs!: QueryList<ElementRef>;
  interval: undefined | number = undefined;
  private fb = inject(FormBuilder);
  stage = signal(1);
  readyToResendIn = signal(5);
  authService = inject(AuthService);
  private router = inject(Router);
  stage1Error = signal('')
  stage2Error = signal('')

  mailForm = this.fb.group({
    email: ['', [Validators.required, Validators.email, Validators.pattern("[a-zA-Z]+.[a-zA-Z]+@htlstp.at")]],
  })

  codeForm = this.fb.group({
    digits: this.fb.array(
      Array(6).fill('').map(() =>
        this.fb.control('', [Validators.required, Validators.pattern('[0-9]')])
      )
    )
  });

  get digits() {
    return this.codeForm.get('digits') as FormArray;
  }

  fullCode() {
    return this.digits.value.join("");
  }

  goToStage(stage: number) {
    this.stage.set(stage);
    if (stage == 2) {
      setTimeout(() => {
        this.inputs.first?.nativeElement.focus();
      })

      this.readyToResendIn.set(5)

      this.interval = setInterval(() => {
        this.readyToResendIn.set(this.readyToResendIn() - 1);
        if (this.readyToResendIn() == 0) {
          clearInterval(this.interval);
        }
      }, 1000)
    }
  }

  verify() {
    if (this.codeForm.invalid) return;
    this.authService.codeSubmit(this.mailForm.controls.email.value!, this.fullCode()).subscribe(
      (res) => {
        if (!res.isSuccess) {
          this.stage2Error.set(res.message)
          return;
        }
        this.router.navigate(['/projects']);
      }
    )
  }

  sendCode() {
    if (this.mailForm.invalid) return;
    this.authService.register(this.mailForm.controls.email.value!).subscribe({
      next: (res) => {
        if (!res.isSuccess) {
          this.stage1Error.set(res.message)
          return;
        }
        this.codeForm.reset();
        this.goToStage(2)
      }
    })
  }

  onInput(e: Event, i: number) {
    const val = (e.target as HTMLInputElement).value;
    if (val && i < 5) {
      this.inputs.toArray()[i + 1].nativeElement.focus();
    }
  }

  onKeydown(e: KeyboardEvent, i: number) {
    if (e.key === 'Backspace' && !this.digits.at(i).value && i > 0) {
      this.inputs.toArray()[i - 1].nativeElement.focus();
    }
  }
}
