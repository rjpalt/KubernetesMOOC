import { test, expect } from '@playwright/test';

test('Todo App loads and displays correct title', async ({ page }) => {
  await page.goto('/');
  await expect(page).toHaveTitle('Todo App with Images');
  await expect(page.locator('h1')).toContainText('Todo App with Hourly Images');
});
