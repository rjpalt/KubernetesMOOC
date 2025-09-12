import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    // Use line reporter for clean terminal output
    ['line'],
    // Generate HTML report but don't start server
    ['html', { open: 'never' }],
    // Custom summary reporter for clear failure visibility
    ['./utils/summary-reporter.ts']
  ],
  use: {
    baseURL: process.env.E2E_BASE_URL || 'http://localhost:8000',
    trace: 'on-first-retry',
  },
  outputDir: 'test-results',
  
  // Global setup for database isolation and health check
  globalSetup: './utils/global-setup.ts',
  
  // Global teardown to prevent hanging processes
  globalTeardown: './utils/global-teardown.ts',
});
