import {Component, ElementRef, inject, QueryList, signal, ViewChild, ViewChildren} from '@angular/core';
import {FormArray, FormBuilder, ReactiveFormsModule, Validators} from '@angular/forms';

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

  mailForm = this.fb.group({
    email: ['', [Validators.required, Validators.email, Validators.pattern("[a-z]+.[a-z]+@htlstp.at")]],
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
  }

  sendCode() {
    if (this.mailForm.invalid) return;
    this.codeForm.reset();
    this.goToStage(2)
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
