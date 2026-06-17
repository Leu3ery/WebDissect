import {ChangeDetectionStrategy, Component, inject} from '@angular/core';
import {LucideCircleCheck, LucideCircleX, LucideInfo, LucideX} from '@lucide/angular';
import {NotificationService} from './notification-service';

@Component({
  selector: 'app-notifications',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [
    LucideCircleCheck,
    LucideCircleX,
    LucideInfo,
    LucideX,
  ],
  templateUrl: './notifications.html',
  styleUrl: './notifications.css',
})
export class Notifications {
  notificationService = inject(NotificationService);

  dismiss(id: number) {
    this.notificationService.dismiss(id);
  }
}
