import {Injectable} from '@angular/core';
import {Observable} from 'rxjs';
import {config} from '../../core/config';

export interface CategoryState {
  status: 'running' | 'done' | 'error';
  count: number;
}

export interface AnalysisEvent {
  type: 'snapshot' | 'start' | 'progress' | 'complete' | 'error';
  category?: string;
  status?: 'running' | 'done' | 'error';
  count?: number;
  message?: string;
  running?: boolean;
  categories?: Record<string, CategoryState>;
}

@Injectable({providedIn: 'root'})
export class AnalysisSocketService {
  /**
   * Opens a WebSocket to stream live analysis progress for a project.
   * The socket is opened on subscribe and closed on unsubscribe.
   */
  connect(projectId: number): Observable<AnalysisEvent> {
    return new Observable<AnalysisEvent>((subscriber) => {
      const proto = location.protocol === 'https:' ? 'wss' : 'ws';
      const token = localStorage.getItem('token') ?? '';
      const url =
        `${proto}://${location.host}${config.apiUrl}` +
        `/projects/${projectId}/analysis/ws?token=${encodeURIComponent(token)}`;

      const ws = new WebSocket(url);

      ws.onmessage = (event) => {
        try {
          subscriber.next(JSON.parse(event.data) as AnalysisEvent);
        } catch {
          // ignore malformed frames
        }
      };
      ws.onerror = () => subscriber.error(new Error('WebSocket error'));

      return () => {
        if (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING) {
          ws.close();
        }
      };
    });
  }
}
