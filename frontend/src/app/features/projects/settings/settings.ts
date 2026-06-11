import {Component, inject, output} from '@angular/core';
import {LucideCircleHelp, LucideKey, LucideLogOut} from "@lucide/angular";
import {AuthService} from '../../../core/services/auth-service';

@Component({
  selector: 'app-settings',
    imports: [
        LucideKey,
        LucideLogOut,
        LucideCircleHelp
    ],
  templateUrl: './settings.html',
  styleUrl: './settings.css',
})
export class Settings {
    authService = inject(AuthService);
    logout = output()
    openChangePassword = output()
    replayTour = output()
}
