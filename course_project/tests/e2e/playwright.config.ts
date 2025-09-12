import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    // Use list reporter for clear test summary with final totals
    ['list'],
    // Generate HTML report but don't start server
    ['html', { open: 'never' }],
    // Add JUnit reporter for structured summary
    ['junit', { outputFile: 'test-results/results.xml' }],
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
