export interface DemoUser {
  readonly id: string;
  readonly label: string;
  readonly beta: boolean;
}

export interface PublicConfig {
  readonly flagsmithApiUrl: string;
  readonly flagsmithClientKey: string;
}

export interface DemoReply {
  readonly userId: string;
  readonly mode: 'legacy' | 'new';
  readonly message: 'Backend: legacy' | 'Backend: new';
}

export interface FrontendState {
  readonly userId: string | null;
  readonly status: 'loading' | 'ready' | 'error';
  readonly enabled: boolean;
  readonly error: string | null;
  readonly evaluatedAt: number | null;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

function invalid(message: string): never {
  throw new Error(message);
}

export function parseDemoUsers(value: unknown): readonly DemoUser[] {
  if (!Array.isArray(value) || value.length !== 20) {
    return invalid('Invalid demo user fixture.');
  }

  const users = value.map((item, index): DemoUser => {
    const number = index + 1;
    const suffix = number.toString().padStart(3, '0');
    const id = isRecord(item) ? item['id'] : undefined;
    const label = isRecord(item) ? item['label'] : undefined;
    const beta = isRecord(item) ? item['beta'] : undefined;
    if (!isRecord(item)
      || id !== `demo-user-${suffix}`
      || label !== `User ${suffix}`
      || beta !== (number <= 5)) {
      return invalid('Invalid demo user fixture.');
    }
    return {
      id,
      label,
      beta
    };
  });
  return users;
}

export function parsePublicConfig(value: unknown): PublicConfig {
  const flagsmithApiUrl = isRecord(value) ? value['flagsmithApiUrl'] : undefined;
  const flagsmithClientKey = isRecord(value) ? value['flagsmithClientKey'] : undefined;
  if (typeof flagsmithApiUrl !== 'string'
    || typeof flagsmithClientKey !== 'string'
    || flagsmithClientKey.trim().length === 0
    || flagsmithClientKey.startsWith('ser.')) {
    return invalid('Invalid Flagsmith client key.');
  }

  let apiUrl: URL;
  try {
    apiUrl = new URL(flagsmithApiUrl);
  } catch {
    return invalid('Invalid private Flagsmith API URL.');
  }

  const loopbackHosts = new Set(['localhost', '127.0.0.1', '[::1]', '::1']);
  if (!loopbackHosts.has(apiUrl.hostname)
    || !['http:', 'https:'].includes(apiUrl.protocol)
    || apiUrl.username !== ''
    || apiUrl.password !== ''
    || apiUrl.search !== ''
    || apiUrl.hash !== ''
    || apiUrl.pathname !== '/api/v1/'
    || flagsmithApiUrl !== apiUrl.toString()) {
    return invalid('Invalid private Flagsmith API URL.');
  }

  return {
    flagsmithApiUrl,
    flagsmithClientKey
  };
}

export function parseDemoReply(value: unknown, expectedUserId: string): DemoReply {
  const userId = isRecord(value) ? value['userId'] : undefined;
  const mode = isRecord(value) ? value['mode'] : undefined;
  const message = isRecord(value) ? value['message'] : undefined;
  if (typeof userId !== 'string'
    || userId !== expectedUserId
    || (mode !== 'legacy' && mode !== 'new')) {
    return invalid('Backend reply does not match the selected user or mode.');
  }
  const expectedMessage = mode === 'legacy' ? 'Backend: legacy' : 'Backend: new';
  if (message !== expectedMessage) {
    return invalid('Backend reply does not match the selected user or mode.');
  }

  return {
    userId,
    mode,
    message: expectedMessage
  };
}
