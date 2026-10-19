import { describe, expect, it } from 'vitest';
import {
  parseDemoReply,
  parseDemoUsers,
  parsePublicConfig
} from './demo-contracts';

function validUsers(): unknown {
  return Array.from({ length: 20 }, (_, index) => {
    const number = index + 1;
    const suffix = number.toString().padStart(3, '0');
    return {
      id: `demo-user-${suffix}`,
      label: `User ${suffix}`,
      beta: number <= 5
    };
  });
}

describe('demo contracts', () => {
  it('parses the fixed twenty-user fixture and rejects an unknown identity', () => {
    const users = parseDemoUsers(validUsers());

    expect(users).toHaveLength(20);
    expect(users[0]).toEqual({
      id: 'demo-user-001',
      label: 'User 001',
      beta: true
    });
    expect(users[4].beta).toBe(true);
    expect(users[5].beta).toBe(false);
    expect(() => parseDemoUsers([{ id: 'not-a-demo-user', label: 'Unknown', beta: false }]))
      .toThrowError(/demo user fixture/i);
  });

  it('requires a non-empty client key and explicit private API URL', () => {
    expect(parsePublicConfig({
      flagsmithApiUrl: 'http://localhost:8000/api/v1/',
      flagsmithClientKey: 'client-key'
    })).toEqual({
      flagsmithApiUrl: 'http://localhost:8000/api/v1/',
      flagsmithClientKey: 'client-key'
    });
    expect(() => parsePublicConfig({
      flagsmithApiUrl: 'https://edge.api.flagsmith.com/api/v1/',
      flagsmithClientKey: 'client-key'
    })).toThrowError(/private/i);
    expect(() => parsePublicConfig({
      flagsmithApiUrl: 'http://localhost:8000/api/v1/',
      flagsmithClientKey: 'ser.server-key'
    })).toThrowError(/client key/i);
    expect(() => parsePublicConfig({
      flagsmithApiUrl: 'http://localhost:8000/api/v1/',
      flagsmithClientKey: ''
    })).toThrowError(/client key/i);
  });

  it('requires the selected user and matching mode/message in backend replies', () => {
    expect(parseDemoReply({
      userId: 'demo-user-001',
      mode: 'new',
      message: 'Backend: new'
    }, 'demo-user-001')).toEqual({
      userId: 'demo-user-001',
      mode: 'new',
      message: 'Backend: new'
    });
    expect(() => parseDemoReply({
      userId: 'demo-user-002',
      mode: 'legacy',
      message: 'Backend: legacy'
    }, 'demo-user-001')).toThrowError(/selected user/i);
    expect(() => parseDemoReply({
      userId: 'demo-user-001',
      mode: 'new',
      message: 'Backend: legacy'
    }, 'demo-user-001')).toThrowError(/mode/i);
  });
});
