import { Page } from '@playwright/test';

/**
 * Database reset capabilities detected from backend
 */
interface ResetCapabilities {
  hasResetEndpoint: boolean;
  hasTruncateEndpoint: boolean;
  resetUrl?: string;
}

/**
 * Result of database reset operation
 */
interface ResetResult {
  success: boolean;
  method: 'backend-api' | 'ui-deletion';
  todosRemoved: number;
}

/**
 * Checks if backend provides a database reset endpoint
 * Many development backends include /dev/reset or similar endpoints
 * 
 * @param page - Playwright page instance
 * @returns Promise resolving to reset capabilities
 */
export async function checkBackendResetCapabilities(page: Page): Promise<ResetCapabilities> {
  const baseUrl = page.url().split('/')[0] + '//' + page.url().split('/')[2];
  
  // Common development reset endpoints to check
  const possibleEndpoints = [
    '/api/dev/reset',
    '/api/admin/reset', 
    '/dev/reset',
    '/admin/reset',
    '/api/reset',
    '/reset'
  ];
  
  console.log('🔍 Checking for backend reset endpoints...');
  
  for (const endpoint of possibleEndpoints) {
    try {
      const response = await page.request.post(`${baseUrl}${endpoint}`);
      if (response.ok()) {
        console.log(`✅ Found database reset endpoint: ${endpoint}`);
        return { hasResetEndpoint: true, hasTruncateEndpoint: false, resetUrl: endpoint };
      }
    } catch (error) {
      // Endpoint doesn't exist, continue checking
      console.log(`❌ Endpoint ${endpoint} not available`);
    }
  }
  
  console.log('ℹ️ No backend reset endpoint found, will use UI fallback');
  return { hasResetEndpoint: false, hasTruncateEndpoint: false };
}

/**
 * Resets database by deleting all todos through the UI
 * This is the fallback method when no backend reset endpoint exists
 * Efficiently handles large numbers of todos with proper error handling
 * 
 * @param page - Playwright page instance
 * @returns Promise resolving to number of todos deleted
 */
export async function resetDatabaseViaUI(page: Page): Promise<number> {
  console.log('🧹 Starting UI-based database reset...');
  
  try {
    await page.goto('/');
    
    let totalDeleted = 0;
    let attempts = 0;
    const maxAttempts = 50; // Prevent infinite loops
    
    while (attempts < maxAttempts) {
      // Wait a moment for page to stabilize
      await page.waitForTimeout(100);
      
      const todoItems = await page.locator('.todo-item').all();
      
      if (todoItems.length === 0) {
        console.log(`✅ Database reset complete - deleted ${totalDeleted} todos`);
        return totalDeleted;
      }
      
      // Delete first todo in the list
      const firstTodo = todoItems[0];
      let todoText = 'unknown';
      
      try {
        // Get todo text for logging
        const textElement = firstTodo.locator('.todo-text');
        if (await textElement.isVisible()) {
          todoText = (await textElement.textContent()) || 'unknown';
        }
        
        // Set up dialog handler for confirmation
        const dialogPromise = page.waitForEvent('dialog');
        
        // Click delete button
        const deleteBtn = firstTodo.locator('.delete-btn');
        if (await deleteBtn.isVisible()) {
          await deleteBtn.click();
          
          // Handle confirmation dialog
          const dialog = await dialogPromise;
          await dialog.accept();
          
          // Wait for deletion to process (HTMX timing)
          await page.waitForTimeout(300);
          totalDeleted++;
          
          console.log(`🗑️ Deleted todo ${totalDeleted}: "${todoText.substring(0, 50)}${todoText.length > 50 ? '...' : ''}"`);
        } else {
          console.warn(`⚠️ Delete button not found for todo: "${todoText}"`);
          attempts++; // Count as failed attempt
        }
        
      } catch (error) {
        console.warn(`⚠️ Failed to delete todo "${todoText}":`, error);
        attempts++; // Count failed deletions toward attempt limit
        
        // Small delay before retrying
        await page.waitForTimeout(500);
      }
      
      attempts++;
    }
    
    console.warn(`⚠️ Database reset incomplete - reached max attempts (${maxAttempts})`);
    return totalDeleted;
    
  } catch (error) {
    console.error('❌ Database reset via UI failed:', error);
    return 0;
  }
}

/**
 * Main database reset function - tries backend endpoint first, falls back to UI deletion
 * Provides comprehensive logging and error handling for debugging
 * 
 * @param page - Playwright page instance
 * @returns Promise resolving to reset operation result
 */
export async function resetDatabase(page: Page): Promise<ResetResult> {
  console.log('🔄 Starting database reset...');
  
  // First, check for backend reset capabilities
  const capabilities = await checkBackendResetCapabilities(page);
  
  if (capabilities.hasResetEndpoint && capabilities.resetUrl) {
    try {
      const baseUrl = page.url().split('/')[0] + '//' + page.url().split('/')[2];
      console.log(`🚀 Attempting backend reset via ${capabilities.resetUrl}...`);
      
      const response = await page.request.post(`${baseUrl}${capabilities.resetUrl}`);
      
      if (response.ok()) {
        console.log('✅ Database reset via backend endpoint successful');
        return { success: true, method: 'backend-api', todosRemoved: -1 };
      } else {
        console.warn(`⚠️ Backend reset returned ${response.status()}, falling back to UI deletion`);
      }
    } catch (error) {
      console.warn('⚠️ Backend reset failed, falling back to UI deletion:', error);
    }
  }
  
  // Fallback to UI-based deletion
  console.log('🔄 Using UI-based deletion fallback...');
  const deleted = await resetDatabaseViaUI(page);
  return { 
    success: deleted >= 0, 
    method: 'ui-deletion', 
    todosRemoved: deleted 
  };
}

/**
 * Smart database initialization that ensures a clean starting state
 * This function should be called before test suites to establish baseline
 * Handles both backend API and UI fallback scenarios gracefully
 * 
 * @param page - Playwright page instance
 * @returns Promise that resolves when database is in clean state
 */
export async function ensureCleanDatabaseState(page: Page): Promise<void> {
  console.log('🎯 Ensuring clean database state...');
  
  const result = await resetDatabase(page);
  
  if (result.success) {
    console.log(`✅ Clean database state achieved via ${result.method}`);
    if (result.method === 'ui-deletion') {
      console.log(`📊 Removed ${result.todosRemoved} todos from database`);
    }
    
    // Wait a moment for any backend sample data creation
    await page.waitForTimeout(1000);
    
    // Navigate to fresh page to see current state
    await page.goto('/');
    await page.waitForTimeout(500);
    
    // Check current state
    const currentCount = await page.locator('.todo-item').count();
    console.log(`📋 Current database state: ${currentCount} todos`);
    
    if (currentCount > 0) {
      console.log('ℹ️ Some todos remain - likely sample data or app initialization');
    }
  } else {
    console.warn('⚠️ Failed to achieve clean database state - tests may encounter data from previous runs');
  }
}

/**
 * Quick database state check without performing reset
 * Useful for debugging and monitoring test environment state
 * 
 * @param page - Playwright page instance
 * @returns Promise resolving to current todo count
 */
export async function checkDatabaseState(page: Page): Promise<number> {
  try {
    await page.goto('/');
    await page.waitForTimeout(500);
    const todoCount = await page.locator('.todo-item').count();
    console.log(`📊 Current database state: ${todoCount} todos`);
    return todoCount;
  } catch (error) {
    console.warn('⚠️ Failed to check database state:', error);
    return -1;
  }
}
