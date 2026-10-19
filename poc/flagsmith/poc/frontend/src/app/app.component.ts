import { HttpClient, HttpParams } from '@angular/common/http';
import {
  ChangeDetectionStrategy,
  Component,
  OnDestroy,
  OnInit,
  computed,
  inject,
  signal
} from '@angular/core';
import { Subscription } from 'rxjs';
import { timeout } from 'rxjs/operators';
import {
  DemoReply,
  DemoUser,
  FrontendState,
  parseDemoReply
} from './demo-contracts';
import { FeatureDemoService } from './feature-demo.service';

@Component({
  selector: 'app-root',
  standalone: true,
  templateUrl: './app.component.html',
  styleUrl: './app.component.css',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class AppComponent implements OnInit, OnDestroy {
  private readonly http = inject(HttpClient);
  readonly featureDemo = inject(FeatureDemoService);

  readonly users = this.featureDemo.users;
  readonly frontendState = this.featureDemo.state;
  readonly selectedUserId = signal('');
  readonly selectedUser = computed(() =>
    this.users().find((user) => user.id === this.selectedUserId()) ?? null
  );
  readonly backendReply = signal<DemoReply | null>(null);
  readonly backendError = signal<string | null>(null);
  readonly backendLoading = signal(false);

  private backendRequest: Subscription | null = null;
  private backendGeneration = 0;
  private destroyed = false;

  ngOnInit(): void {
    void this.initializePage();
  }

  ngOnDestroy(): void {
    this.destroyed = true;
    this.backendGeneration++;
    this.backendRequest?.unsubscribe();
    this.backendRequest = null;
  }

  async initializePage(): Promise<void> {
    await this.featureDemo.initialize();
    if (this.destroyed) return;

    const userId = this.frontendState().userId ?? this.users()[0]?.id;
    if (userId !== undefined) this.selectedUserId.set(userId);
  }

  onUserChange(userId: string): void {
    this.invalidateBackendRequest();
    const user = this.users().find((candidate) => candidate.id === userId);
    if (!user) {
      this.selectedUserId.set('');
      return;
    }

    this.selectedUserId.set(user.id);
    void this.featureDemo.selectUser(user);
  }

  callBackend(): void {
    const user = this.selectedUser();
    if (!user) return;

    this.backendRequest?.unsubscribe();
    const generation = ++this.backendGeneration;
    const userId = user.id;
    this.backendReply.set(null);
    this.backendError.set(null);
    this.backendLoading.set(true);

    const params = new HttpParams().set('userId', userId);
    this.backendRequest = this.http.get<unknown>('/api/demo', { params })
      .pipe(timeout({ each: 2_000 }))
      .subscribe({
        next: (value) => {
          if (!this.isCurrentBackendRequest(generation, userId)) return;
          try {
            const reply = parseDemoReply(value, userId);
            this.backendReply.set(reply);
            this.backendLoading.set(false);
          } catch (error) {
            this.publishBackendError(error, generation, userId);
          }
        },
        error: (error: unknown) => {
          this.publishBackendError(error, generation, userId);
        }
      });
  }

  backendResultText(): string {
    const reply = this.backendReply();
    return reply === null ? '' : `${reply.message} (${reply.userId})`;
  }

  private invalidateBackendRequest(): void {
    this.backendGeneration++;
    this.backendRequest?.unsubscribe();
    this.backendRequest = null;
    this.backendReply.set(null);
    this.backendError.set(null);
    this.backendLoading.set(false);
  }

  private publishBackendError(
    error: unknown,
    generation: number,
    userId: string
  ): void {
    if (!this.isCurrentBackendRequest(generation, userId)) return;
    this.backendReply.set(null);
    this.backendLoading.set(false);
    this.backendError.set(this.sanitizeBackendError(error));
  }

  private sanitizeBackendError(error: unknown): string {
    if (error instanceof Error && error.message.includes('selected user')) {
      return error.message;
    }
    return 'Backend request failed.';
  }

  private isCurrentBackendRequest(generation: number, userId: string): boolean {
    return !this.destroyed
      && generation === this.backendGeneration
      && this.selectedUserId() === userId;
  }
}
