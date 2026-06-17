import {Injectable, signal} from '@angular/core';

export type NotificationType = 'success' | 'error' | 'info';

export interface Notification {
  id: number;
  type: NotificationType;
  message: string;
}

@Injectable({
  providedIn: 'root',
})
export class NotificationService {
  private _notifications = signal<Notification[]>([]);
  readonly notifications = this._notifications.asReadonly();
  private nextId = 0;
  private readonly duration = 3000;

  success(message: string) {
    this.show('success', message);
  }

  error(message: string) {
    this.show('error', message);
  }

  info(message: string) {
    this.show('info', message);
  }

  show(type: NotificationType, message: string) {
    const id = this.nextId++;
    this._notifications.update(list => [...list, {id, type, message}]);
    setTimeout(() => this.dismiss(id), this.duration);
  }

  dismiss(id: number) {
    this._notifications.update(list => list.filter(n => n.id !== id));
  }
}
