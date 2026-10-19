import { provideHttpClient } from '@angular/common/http';
import {
  provideHttpClientTesting,
  HttpTestingController,
  TestRequest
} from '@angular/common/http/testing';
import { provideZonelessChangeDetection } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { signal } from '@angular/core';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import {
  DemoReply,
  DemoUser,
  FrontendState
} from './demo-contracts';
import { AppComponent } from './app.component';
import { FeatureDemoService } from './feature-demo.service';

const USERS: readonly DemoUser[] = Array.from({ length: 20 }, (_, index) => {
  const number = index + 1;
  const suffix = number.toString().padStart(3, '0');
  return {
    id: `demo-user-${suffix}`,
    label: `User ${suffix}`,
    beta: number <= 5
  };
});

const INITIAL_STATE: FrontendState = {
  userId: 'demo-user-001',
  status: 'ready',
  enabled: false,
  error: null,
  evaluatedAt: 0
};

class FakeFeatureDemoService {
  readonly users = signal<readonly DemoUser[]>(USERS);
  readonly state = signal<FrontendState>(INITIAL_STATE);
  readonly initialize = vi.fn(async (): Promise<void> => undefined);
  readonly selectUser = vi.fn(async (user: DemoUser): Promise<void> => {
    this.state.set({
      userId: user.id,
      status: 'ready',
      enabled: this.state().enabled,
      error: null,
      evaluatedAt: 0
    });
  });

  enabled(): boolean {
    const current = this.state();
    return current.status === 'ready' && current.enabled;
  }

  setFrontendState(state: FrontendState): void {
    this.state.set(state);
  }

  setReadyState(enabled: boolean): void {
    this.setFrontendState({
      userId: this.state().userId,
      status: 'ready',
      enabled,
      error: null,
      evaluatedAt: 0
    });
  }
}

describe('AppComponent', () => {
  let fixture: ComponentFixture<AppComponent>;
  let http: HttpTestingController;
  let featureDemo: FakeFeatureDemoService;

  beforeEach(() => {
    featureDemo = new FakeFeatureDemoService();
    TestBed.configureTestingModule({
      imports: [AppComponent],
      providers: [
        provideZonelessChangeDetection(),
        provideHttpClient(),
        provideHttpClientTesting(),
        { provide: FeatureDemoService, useValue: featureDemo }
      ]
    });
    fixture = TestBed.createComponent(AppComponent);
    http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
  });

  afterEach(() => {
    http.verify({ ignoreCancelled: true });
    TestBed.resetTestingModule();
  });

  async function settle(): Promise<void> {
    await fixture.whenStable();
    fixture.detectChanges();
  }

  function byTestId<T extends HTMLElement>(testId: string): T {
    const element = fixture.nativeElement.querySelector(`[data-testid="${testId}"]`);
    if (!(element instanceof HTMLElement)) {
      throw new Error(`Missing test element: ${testId}`);
    }
    return element as T;
  }

  function selectUser(userId: string): void {
    const select = byTestId<HTMLSelectElement>('demo-user');
    select.value = userId;
    select.dispatchEvent(new Event('change'));
    fixture.detectChanges();
  }

  function callBackend(): void {
    byTestId<HTMLButtonElement>('call-backend').click();
    fixture.detectChanges();
  }

  function frontendSection(): HTMLElement {
    const section = fixture.nativeElement.querySelector('.frontend-state');
    if (!(section instanceof HTMLElement)) {
      throw new Error('Missing frontend state section');
    }
    return section;
  }

  it('uses the fixed initial user and starts with an empty backend result', async () => {
    await settle();

    expect(byTestId<HTMLSelectElement>('demo-user').value).toBe('demo-user-001');
    expect(byTestId('backend-result').textContent?.trim()).toBe('');
    expect(byTestId('backend-error').textContent?.trim()).toBe('');
  });

  it.each([
    { frontendEnabled: false, backendMode: 'legacy' as const },
    { frontendEnabled: false, backendMode: 'new' as const },
    { frontendEnabled: true, backendMode: 'legacy' as const },
    { frontendEnabled: true, backendMode: 'new' as const }
  ])(
    'renders frontend $frontendEnabled independently from backend $backendMode',
    async ({ frontendEnabled, backendMode }) => {
      await settle();
      featureDemo.setReadyState(frontendEnabled);
      fixture.detectChanges();

      callBackend();
      const request = http.expectOne((candidate) =>
        candidate.url === '/api/demo'
        && candidate.method === 'GET'
        && candidate.params.get('userId') === 'demo-user-001'
      );
      expect(request.request.params.keys()).toEqual(['userId']);
      expect(request.request.body).toBeNull();

      const reply: DemoReply = {
        userId: 'demo-user-001',
        mode: backendMode,
        message: backendMode === 'new' ? 'Backend: new' : 'Backend: legacy'
      };
      request.flush(reply);
      await settle();

      expect(byTestId('frontend-result').textContent).toContain(
        frontendEnabled ? 'Frontend: new' : 'Frontend: legacy'
      );
      expect(byTestId('backend-result').textContent).toContain(reply.message);
    }
  );

  it('renders loading separately without labeling it legacy', async () => {
    await settle();
    featureDemo.setFrontendState({
      ...INITIAL_STATE,
      status: 'loading',
      enabled: false,
      evaluatedAt: null
    });
    fixture.detectChanges();

    expect(byTestId('frontend-result').textContent?.trim()).toBe('Frontend loading…');
    expect(byTestId('frontend-result').textContent).not.toContain('Frontend: legacy');
    expect(frontendSection().classList.contains('frontend-state--legacy')).toBe(false);
    expect(frontendSection().classList.contains('frontend-state--new')).toBe(false);
  });

  it('renders SDK errors as unavailable instead of labeling them legacy', async () => {
    await settle();
    featureDemo.setFrontendState({
      ...INITIAL_STATE,
      status: 'error',
      enabled: false,
      error: 'Frontend flag service is unavailable.',
      evaluatedAt: null
    });
    fixture.detectChanges();

    expect(byTestId('frontend-result').textContent?.trim()).toBe('Frontend unavailable.');
    expect(byTestId('frontend-result').textContent).not.toContain('Frontend: legacy');
    expect(byTestId('frontend-error').textContent).toContain(
      'Frontend flag service is unavailable.'
    );
    expect(frontendSection().classList.contains('frontend-state--legacy')).toBe(false);
    expect(frontendSection().classList.contains('frontend-state--new')).toBe(false);
  });

  it('renders an expired decision as unavailable instead of labeling it legacy', async () => {
    await settle();
    featureDemo.setFrontendState({
      ...INITIAL_STATE,
      status: 'error',
      enabled: false,
      error: 'Frontend flag decision expired.',
      evaluatedAt: null
    });
    fixture.detectChanges();

    expect(byTestId('frontend-result').textContent?.trim()).toBe('Frontend unavailable.');
    expect(byTestId('frontend-result').textContent).not.toContain('Frontend: legacy');
    expect(byTestId('frontend-error').textContent).toContain(
      'Frontend flag decision expired.'
    );
  });

  it('renders a switching user as loading instead of labeling it legacy', async () => {
    await settle();
    featureDemo.setFrontendState({
      userId: 'demo-user-002',
      status: 'loading',
      enabled: false,
      error: null,
      evaluatedAt: null
    });
    fixture.detectChanges();

    expect(byTestId('frontend-result').textContent?.trim()).toBe('Frontend loading…');
    expect(byTestId('frontend-result').textContent).not.toContain('Frontend: legacy');
    expect(frontendSection().classList.contains('frontend-state--legacy')).toBe(false);
    expect(frontendSection().classList.contains('frontend-state--new')).toBe(false);
  });

  it('renders ready-off as the exact legacy frontend state', async () => {
    await settle();
    featureDemo.setReadyState(false);
    fixture.detectChanges();

    expect(byTestId('frontend-result').textContent?.trim()).toBe('Frontend: legacy');
    expect(frontendSection().classList.contains('frontend-state--legacy')).toBe(true);
    expect(frontendSection().classList.contains('frontend-state--new')).toBe(false);
  });

  it('shows a sanitized backend error instead of a fabricated response', async () => {
    await settle();
    callBackend();
    const request = http.expectOne('/api/demo?userId=demo-user-001');

    request.flush({ detail: 'internal server details' }, {
      status: 503,
      statusText: 'Service Unavailable'
    });
    await settle();

    expect(byTestId('backend-result').textContent?.trim()).toBe('');
    expect(byTestId('backend-error').textContent).toContain('Backend request failed.');
    expect(byTestId('backend-error').textContent).not.toContain('internal server details');
  });

  it('rejects a backend reply for a different user', async () => {
    await settle();
    callBackend();
    const request = http.expectOne('/api/demo?userId=demo-user-001');

    request.flush({
      userId: 'demo-user-002',
      mode: 'legacy',
      message: 'Backend: legacy'
    });
    await settle();

    expect(byTestId('backend-result').textContent?.trim()).toBe('');
    expect(byTestId('backend-error').textContent).toContain('selected user');
  });

  it('clears the previous backend result immediately when the user changes', async () => {
    await settle();
    callBackend();
    const request = http.expectOne('/api/demo?userId=demo-user-001');
    request.flush({
      userId: 'demo-user-001',
      mode: 'new',
      message: 'Backend: new'
    });
    await settle();
    expect(byTestId('backend-result').textContent).toContain('Backend: new');

    selectUser('demo-user-002');

    expect(byTestId('backend-result').textContent?.trim()).toBe('');
    expect(byTestId('backend-error').textContent?.trim()).toBe('');
  });

  it('cancels a delayed old request and only publishes the new user response', async () => {
    await settle();
    callBackend();
    const oldRequest = http.expectOne('/api/demo?userId=demo-user-001');

    selectUser('demo-user-002');
    expect(oldRequest.cancelled).toBe(true);

    callBackend();
    const newRequest = http.expectOne('/api/demo?userId=demo-user-002');
    newRequest.flush({
      userId: 'demo-user-002',
      mode: 'legacy',
      message: 'Backend: legacy'
    });
    await settle();

    expect(byTestId('backend-result').textContent).toContain('Backend: legacy');
    expect(byTestId('backend-result').textContent).not.toContain('demo-user-001');
  });
});
