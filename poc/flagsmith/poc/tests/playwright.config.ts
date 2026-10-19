import { defineConfig, devices } from '../frontend/node_modules/@playwright/test';
import { resolve } from 'node:path';

const pocDirectory = resolve(process.cwd(), '..');
const testsDirectory = resolve(pocDirectory, 'tests');

export default defineConfig({
  testDir: testsDirectory,
  fullyParallel: false,
  reporter: 'list',
  use: {
    baseURL: 'http://localhost:4200',
    trace: 'retain-on-failure'
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] }
    }
  ],
  webServer: {
    command: 'npm.cmd start -- --host localhost --port 4200',
    cwd: resolve(pocDirectory, 'frontend'),
    url: 'http://localhost:4200',
    reuseExistingServer: false,
    timeout: 120_000
  }
});
