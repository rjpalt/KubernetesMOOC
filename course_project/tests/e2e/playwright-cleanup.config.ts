import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  // Run cleanup tests sequentially to prevent test isolation issues
  fullyParallel: false,
  workers: 1,
  forbidOnly: false,
  retries: 0,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:8000',
    trace: 'on-first-retry',
  },
  outputDir: 'test-results',
  // Only run cleanup-related tests
  testMatch: ['**/cleanup-helpers-validation.spec.ts', '**/enhanced-cleanup-validation.spec.ts'],
});
