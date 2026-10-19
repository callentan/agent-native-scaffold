import {
  expect,
  test,
  type Page
} from '../frontend/node_modules/@playwright/test';

const USERS = Array.from({ length: 20 }, (_, index) => {
  const number = index + 1;
  const suffix = number.toString().padStart(3, '0');
  return {
    id: `demo-user-${suffix}`,
    label: `User ${suffix}`,
    beta: number <= 5
  };
});

const corsHeaders = {
  'access-control-allow-origin': 'http://localhost:4200',
  'access-control-allow-methods': 'GET, POST, OPTIONS',
  'access-control-allow-headers': 'content-type, x-environment-key',
  'access-control-max-age': '60'
};

interface ControlledScenario {
  readonly frontendEnabled: boolean;
  readonly backendMode: 'legacy' | 'new';
  readonly backendStatus?: number;
  readonly responseUserId?: string;
  readonly delayedUserId?: string;
}

interface ControlledNetwork {
  readonly requests: readonly CapturedRequest[];
  readonly backendRequests: URL[];
  readonly flagsmithRequests: URL[];
  readonly inspectedResponseBodies: string[];
}

interface CapturedRequest {
  readonly method: string;
  readonly origin: string;
  readonly pathname: string;
  readonly queryKeys: readonly string[];
}

export function assertStableExpansion(
  tenPercent: ReadonlySet<string>,
  fiftyPercent: ReadonlySet<string>,
  hundredPercent: ReadonlySet<string>,
  allUsers: ReadonlySet<string>
): void {
  for (const id of tenPercent) {
    expect(fiftyPercent.has(id)).toBe(true);
  }
  expect([...hundredPercent].sort()).toEqual([...allUsers].sort());
}

test('accepts manually specified stable rollout cohorts', () => {
  const tenPercent = new Set(['demo-user-003']);
  const fiftyPercent = new Set([
    'demo-user-003',
    'demo-user-011',
    'demo-user-017',
    'demo-user-019'
  ]);
  const hundredPercent = new Set([
    'demo-user-001',
    'demo-user-002',
    'demo-user-003',
    'demo-user-004',
    'demo-user-005',
    'demo-user-006',
    'demo-user-007',
    'demo-user-008',
    'demo-user-009',
    'demo-user-010',
    'demo-user-011',
    'demo-user-012',
    'demo-user-013',
    'demo-user-014',
    'demo-user-015',
    'demo-user-016',
    'demo-user-017',
    'demo-user-018',
    'demo-user-019',
    'demo-user-020'
  ]);
  const allUsers = new Set([
    'demo-user-001',
    'demo-user-002',
    'demo-user-003',
    'demo-user-004',
    'demo-user-005',
    'demo-user-006',
    'demo-user-007',
    'demo-user-008',
    'demo-user-009',
    'demo-user-010',
    'demo-user-011',
    'demo-user-012',
    'demo-user-013',
    'demo-user-014',
    'demo-user-015',
    'demo-user-016',
    'demo-user-017',
    'demo-user-018',
    'demo-user-019',
    'demo-user-020'
  ]);

  expect(() => assertStableExpansion(
    tenPercent,
    fiftyPercent,
    hundredPercent,
    allUsers
  )).not.toThrow();

  expect(() => assertStableExpansion(
    new Set(['demo-user-003']),
    new Set([
      'demo-user-011',
      'demo-user-017',
      'demo-user-019'
    ]),
    hundredPercent,
    allUsers
  )).toThrow();

  expect(() => assertStableExpansion(
    tenPercent,
    fiftyPercent,
    new Set([
      'demo-user-001',
      'demo-user-002',
      'demo-user-003',
      'demo-user-004',
      'demo-user-005',
      'demo-user-006',
      'demo-user-007',
      'demo-user-008',
      'demo-user-009',
      'demo-user-010',
      'demo-user-011',
      'demo-user-012',
      'demo-user-013',
      'demo-user-014',
      'demo-user-015',
      'demo-user-016',
      'demo-user-017',
      'demo-user-018',
      'demo-user-019'
    ]),
    allUsers
  )).toThrow();

  expect(() => assertStableExpansion(
    tenPercent,
    fiftyPercent,
    new Set([
      'demo-user-001',
      'demo-user-002',
      'demo-user-003',
      'demo-user-004',
      'demo-user-005',
      'demo-user-006',
      'demo-user-007',
      'demo-user-008',
      'demo-user-009',
      'demo-user-010',
      'demo-user-011',
      'demo-user-012',
      'demo-user-013',
      'demo-user-014',
      'demo-user-015',
      'demo-user-016',
      'demo-user-017',
      'demo-user-018',
      'demo-user-019',
      'demo-user-020',
      'demo-user-021'
    ]),
    allUsers
  )).toThrow();
});

async function installControlledRoutes(
  page: Page,
  scenario: ControlledScenario
): Promise<ControlledNetwork> {
  const requests: CapturedRequest[] = [];
  const backendRequests: URL[] = [];
  const flagsmithRequests: URL[] = [];
  const inspectedResponseBodies: string[] = [];
  const network = {
    requests,
    backendRequests,
    flagsmithRequests,
    inspectedResponseBodies
  };

  page.on('request', (request) => {
    const requestUrl = new URL(request.url());
    requests.push({
      method: request.method(),
      origin: requestUrl.origin,
      pathname: requestUrl.pathname,
      queryKeys: [...requestUrl.searchParams.keys()]
    });
  });
  page.on('response', (response) => {
    if (response.url().endsWith('/poc-config.json')
      || response.url().includes('localhost:8000/api/v1/')) {
      void response.text()
        .then((body) => inspectedResponseBodies.push(body))
        .catch(() => undefined);
    }
  });

  await page.route(/http:\/\/localhost:4200\/api\/.*/, async (route) => {
    const requestUrl = new URL(route.request().url());
    if (requestUrl.pathname !== '/api/demo' || route.request().method() !== 'GET') {
      await route.abort();
      return;
    }

    backendRequests.push(requestUrl);
    const userId = requestUrl.searchParams.get('userId');
    if (scenario.delayedUserId === userId) {
      await new Promise((resolveDelay) => setTimeout(resolveDelay, 500));
    }

    if (scenario.backendStatus !== undefined) {
      await route.fulfill({
        status: scenario.backendStatus,
        contentType: 'application/problem+json',
        body: JSON.stringify({
          title: 'Internal backend details that must not reach the UI.'
        }),
        headers: { 'cache-control': 'no-store' }
      }).catch(() => undefined);
      return;
    }

    const responseUserId = scenario.responseUserId ?? userId;
    const message = scenario.backendMode === 'new' ? 'Backend: new' : 'Backend: legacy';
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        userId: responseUserId,
        mode: scenario.backendMode,
        message
      }),
      headers: { 'cache-control': 'no-store' }
    }).catch(() => undefined);
  });

  await page.route('**/demo-users.json', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(USERS)
    });
  });

  await page.route('**/poc-config.json', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        flagsmithApiUrl: 'http://localhost:8000/api/v1/',
        flagsmithClientKey: 'client-public-key'
      })
    });
  });

  await page.route(/http:\/\/localhost:8000\/api\/v1\/.*/, async (route) => {
    const request = route.request();
    const requestUrl = new URL(request.url());
    flagsmithRequests.push(requestUrl);
    if (request.method() === 'OPTIONS') {
      await route.fulfill({
        status: 204,
        headers: corsHeaders
      });
      return;
    }

    if (request.method() !== 'POST' || requestUrl.pathname !== '/api/v1/identities/') {
      await route.abort();
      return;
    }

    const body = JSON.parse(request.postData() ?? '{}') as {
      identifier?: string;
      traits?: readonly { trait_key?: string; trait_value?: unknown }[];
    };
    const userId = body.identifier ?? '';
    const beta = USERS.find((user) => user.id === userId)?.beta ?? false;
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      headers: corsHeaders,
      body: JSON.stringify({
        identifier: userId,
        traits: [{ trait_key: 'beta', trait_value: beta }],
        flags: [{
          enabled: scenario.frontendEnabled,
          feature_state_value: null,
          feature: { id: 1, name: 'frontend_demo_v2' }
        }]
      })
    });
  });

  return network;
}

function assertBusinessApiBoundary(network: ControlledNetwork): void {
  const browserApiRequests = network.requests.filter((request) =>
    request.origin === 'http://localhost:4200'
    && request.pathname.startsWith('/api/')
  );

  expect(browserApiRequests.every((request) =>
    request.method === 'GET'
    && request.pathname === '/api/demo'
    && request.queryKeys.length === 1
    && request.queryKeys[0] === 'userId'
  )).toBe(true);
  expect(browserApiRequests).toEqual(
    browserApiRequests.filter((request) =>
      request.method === 'GET'
      && request.pathname === '/api/demo'
      && request.queryKeys.length === 1
      && request.queryKeys[0] === 'userId'
    )
  );
}

async function openControlledPage(
  page: Page,
  scenario: ControlledScenario
): Promise<ControlledNetwork> {
  const network = await installControlledRoutes(page, scenario);
  await page.goto('/');
  await expect(page.getByTestId('demo-user')).toHaveValue('demo-user-001');
  return network;
}

test('initial user is fixed and backend result starts empty', async ({ page }) => {
  const network = await openControlledPage(page, {
    frontendEnabled: false,
    backendMode: 'legacy'
  });

  await expect(page.getByTestId('backend-result')).toBeEmpty();
  assertBusinessApiBoundary(network);
});

for (const combination of [
  { frontendEnabled: false, backendMode: 'legacy' as const },
  { frontendEnabled: false, backendMode: 'new' as const },
  { frontendEnabled: true, backendMode: 'legacy' as const },
  { frontendEnabled: true, backendMode: 'new' as const }
]) {
  test(`renders the independent ${combination.frontendEnabled ? 'new' : 'legacy'} frontend and ${combination.backendMode} backend`, async ({ page }) => {
    const network = await openControlledPage(page, combination);

    await expect(page.getByTestId('frontend-result')).toHaveText(
      combination.frontendEnabled ? 'Frontend: new' : 'Frontend: legacy'
    );
    await page.getByTestId('call-backend').click();
    await expect(page.getByTestId('backend-result')).toContainText(
      combination.backendMode === 'new' ? 'Backend: new' : 'Backend: legacy'
    );

    const backendRequest = network.backendRequests[0];
    expect(network.flagsmithRequests.length).toBeGreaterThan(0);
    expect(network.flagsmithRequests.every((request) =>
      request.origin === 'http://localhost:8000'
      && request.pathname === '/api/v1/identities/'
    )).toBe(true);
    expect(backendRequest.pathname).toBe('/api/demo');
    expect([...backendRequest.searchParams.keys()]).toEqual(['userId']);
    expect(backendRequest.searchParams.get('userId')).toBe('demo-user-001');
    assertBusinessApiBoundary(network);
    await expect.poll(() => network.inspectedResponseBodies.join('\n')).not.toContain('ser.');
    await expect.poll(() => network.inspectedResponseBodies.join('\n'))
      .not.toContain('backend_demo_v2');
  });
}

test('submits the exact selected user and clears the previous backend result immediately', async ({ page }) => {
  const network = await openControlledPage(page, {
    frontendEnabled: true,
    backendMode: 'new'
  });

  await page.getByTestId('call-backend').click();
  await expect(page.getByTestId('backend-result')).toContainText('Backend: new');
  await page.getByTestId('demo-user').selectOption('demo-user-002');

  await expect(page.getByTestId('backend-result')).toBeEmpty();
  await page.getByTestId('call-backend').click();
  await expect(page.getByTestId('backend-result')).toContainText('demo-user-002');
  expect(network.backendRequests.map((request) =>
    request.searchParams.get('userId')
  )).toEqual(['demo-user-001', 'demo-user-002']);
  assertBusinessApiBoundary(network);
});

test('displays a sanitized backend error', async ({ page }) => {
  const network = await openControlledPage(page, {
    frontendEnabled: false,
    backendMode: 'legacy',
    backendStatus: 503
  });

  await page.getByTestId('call-backend').click();
  await expect(page.getByTestId('backend-error')).toHaveText('Backend request failed.');
  await expect(page.getByTestId('backend-result')).toBeEmpty();
  await expect(page.getByTestId('backend-error')).not.toContainText('Internal backend details');
  assertBusinessApiBoundary(network);
});

test('rejects a backend response for a different user', async ({ page }) => {
  const network = await openControlledPage(page, {
    frontendEnabled: true,
    backendMode: 'new',
    responseUserId: 'demo-user-002'
  });

  await page.getByTestId('call-backend').click();
  await expect(page.getByTestId('backend-error')).toContainText('selected user');
  await expect(page.getByTestId('backend-result')).toBeEmpty();
  assertBusinessApiBoundary(network);
});

test('does not publish a delayed user-A response after selecting user B', async ({ page }) => {
  const network = await openControlledPage(page, {
    frontendEnabled: true,
    backendMode: 'new',
    delayedUserId: 'demo-user-001'
  });

  await page.getByTestId('call-backend').click();
  await page.getByTestId('demo-user').selectOption('demo-user-002');
  await expect(page.getByTestId('backend-result')).toBeEmpty();
  await page.getByTestId('call-backend').click();
  await expect(page.getByTestId('backend-result')).toContainText('demo-user-002');

  await page.waitForTimeout(700);
  await expect(page.getByTestId('backend-result')).toContainText('demo-user-002');
  await expect(page.getByTestId('backend-result')).not.toContainText('demo-user-001');
  expect(network.backendRequests.map((request) =>
    request.searchParams.get('userId')
  )).toEqual(['demo-user-001', 'demo-user-002']);
  assertBusinessApiBoundary(network);
});
