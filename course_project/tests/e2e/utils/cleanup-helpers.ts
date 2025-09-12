import { Page, expect } from '@playwright/test';

/**
 * Environment detection and cleanup strategy configuration
 */
interface CleanupConfig {
  isCleanSlateEnvironment: boolean;
  requiresAggressiveCleanup: boolean;
  allowSampleDataPreservation: boolean;
}

/**
 * Detects the testing environment and returns appropriate cleanup configuration
 */
async function getCleanupConfig(page: Page): Promise<CleanupConfig> {
  try {
    // Check if we're in a Docker environment (clean slate)
    const currentUrl = page.url();
    const isDocker = currentUrl.includes('localhost') || currentUrl.includes('127.0.0.1') || currentUrl.includes('todo-app-fe:8000');
    
    // Check for feature branch environment markers
    const isFeatureBranch = currentUrl.includes('feature-') || currentUrl.includes('/feature/');
    
    if (isDocker) {
      return {
        isCleanSlateEnvironment: true,
        requiresAggressiveCleanup: false,
        allowSampleDataPreservation: true
      };
    } else if (isFeatureBranch) {
      return {
        isCleanSlateEnvironment: false,
        requiresAggressiveCleanup: true,
        allowSampleDataPreservation: false
      };
    } else {
      // Production or unknown environment - be conservative
      return {
        isCleanSlateEnvironment: false,
        requiresAggressiveCleanup: false,
        allowSampleDataPreservation: true
      };
    }
  } catch (error) {
    console.warn('Failed to detect environment, using conservative cleanup:', error);
    return {
      isCleanSlateEnvironment: false,
      requiresAggressiveCleanup: false,
      allowSampleDataPreservation: true
    };
  }
}

/**
 * Creates a todo item and returns its ID for tracking
 * @param page - Playwright page object
 * @param text - Text content for the todo
 * @returns Promise<string> - The todo ID for tracking
 */
export async function createTodoAndTrack(page: Page, text: string): Promise<string> {
  try {
    // Navigate to home page if not already there
    await page.goto('/');
    
    // First check if this exact todo already exists and clear duplicates
    // Use normalized text comparison to handle whitespace issues
    const normalizedInputText = text.trim().replace(/\s+/g, ' ');
    
    const allTodoItems = await page.locator('.todo-item').all();
    const duplicatesToDelete: string[] = [];
    
    for (const todoItem of allTodoItems) {
      try {
        const existingText = await todoItem.locator('.todo-text').textContent();
        if (existingText) {
          const normalizedExistingText = existingText.trim().replace(/\s+/g, ' ');
          if (normalizedExistingText === normalizedInputText) {
            duplicatesToDelete.push(normalizedExistingText);
          }
        }
      } catch (error) {
        // Skip this todo item if we can't read its text
        continue;
      }
    }
    
    if (duplicatesToDelete.length > 0) {
      console.warn(`Found ${duplicatesToDelete.length} existing todos with text "${normalizedInputText}" - cleaning up duplicates first`);
      
      // Set up dialog handler for deletion confirmations
      const dialogHandler = (dialog: any) => dialog.accept();
      page.on('dialog', dialogHandler);
      
      // Delete all existing todos with this text using a more reliable approach
      for (let attempt = 0; attempt < 3 && duplicatesToDelete.length > 0; attempt++) {
        const remainingTodos = await page.locator('.todo-item').all();
        let deletedInThisAttempt = 0;
        
        for (const todoItem of remainingTodos) {
          try {
            const existingText = await todoItem.locator('.todo-text').textContent();
            if (existingText) {
              const normalizedExistingText = existingText.trim().replace(/\s+/g, ' ');
              if (normalizedExistingText === normalizedInputText && await todoItem.isVisible({ timeout: 500 })) {
                await todoItem.locator('.delete-btn').click();
                await page.waitForTimeout(300);
                deletedInThisAttempt++;
                console.log(`Deleted duplicate todo: "${normalizedExistingText}"`);
              }
            }
          } catch (deleteError) {
            console.warn(`Failed to delete duplicate todo:`, deleteError);
          }
        }
        
        if (deletedInThisAttempt === 0) {
          break; // No more duplicates found
        }
        
        // Wait before next attempt
        await page.waitForTimeout(500);
      }
      
      // Remove dialog handler
      page.off('dialog', dialogHandler);
      
      // Wait for deletions to complete
      await page.waitForTimeout(1000);
    }
    
    // Fill todo input with provided text
    await page.fill('#todo-input', text);
    
    // Click submit button
    await page.click('button[type="submit"]');
    
    // Wait for todo to appear in DOM
    await page.waitForTimeout(1000);
    
    // Wait for the NEW todo item to be visible
    // Use a more flexible locator that handles whitespace variations
    const todoItem = page.locator('.todo-item').filter({
      has: page.locator('.todo-text')
    }).first();
    
    await todoItem.waitFor({ state: 'visible', timeout: 5000 });
    
    // Extract the actual text as it appears in the DOM for cleanup tracking
    const actualTodoText = await todoItem.locator('.todo-text').textContent();
    if (!actualTodoText) {
      throw new Error(`Failed to get todo text for created todo: ${text}`);
    }
    
    // Return the actual text from DOM (which may have different whitespace)
    // This ensures our cleanup functions can find it later
    const cleanText = actualTodoText.trim();
    
    console.log(`Created todo with text: "${cleanText}" (normalized from input: "${normalizedInputText}")`);
    return cleanText;
    
  } catch (error) {
    console.warn(`Failed to create and track todo "${text}":`, error);
    throw new Error(`Failed to create todo: ${error}`);
  }
}

/**
 * Deletes specific todos created during a test
 * @param page - Playwright page object
 * @param todoIds - Array of todo IDs (text content) to delete
 */
export async function cleanupTestTodos(page: Page, todoIds: string[]): Promise<void> {
  if (todoIds.length === 0) {
    return;
  }
  
  // Setup dialog handler to automatically accept confirmation dialogs
  const dialogHandler = (dialog: any) => dialog.accept();
  
  try {
    // Navigate to home page if needed
    await page.goto('/');
    
    page.on('dialog', dialogHandler);
    
    console.log(`Starting cleanup of ${todoIds.length} todos: ${todoIds.map(id => `"${id}"`).join(', ')}`);
    
    for (const todoId of todoIds) {
      try {
        // Normalize the todo ID text for comparison
        const normalizedTodoId = todoId.trim().replace(/\s+/g, ' ');
        
        // Find all todos that might match (handle whitespace variations)
        const allTodoItems = await page.locator('.todo-item').all();
        let todoFound = false;
        
        for (const todoItem of allTodoItems) {
          try {
            if (!(await todoItem.isVisible({ timeout: 500 }))) {
              continue;
            }
            
            const todoText = await todoItem.locator('.todo-text').textContent();
            if (todoText) {
              const normalizedTodoText = todoText.trim().replace(/\s+/g, ' ');
              
              // Check if this todo matches what we're looking for
              if (normalizedTodoText === normalizedTodoId) {
                todoFound = true;
                
                // Get the todo ID for verification
                const htmlTodoId = await todoItem.getAttribute('data-todo-id');
                
                // Click delete button
                const deleteBtn = todoItem.locator('.delete-btn');
                await deleteBtn.click();
                
                // Wait for HTMX to process the request
                await page.waitForTimeout(1000);
                
                // Verify deletion by checking if the todo with the specific ID no longer exists
                if (htmlTodoId) {
                  const todoStillExists = await page.locator(`#todo-${htmlTodoId}`).isVisible({ timeout: 1000 }).catch(() => false);
                  
                  if (!todoStillExists) {
                    console.log(`Successfully cleaned up todo: "${normalizedTodoId}"`);
                    break; // Successfully deleted, move to next todo
                  } else {
                    console.warn(`Todo "${normalizedTodoId}" still visible after deletion attempt, retrying once`);
                    // Try clicking delete one more time
                    try {
                      if (await todoItem.isVisible({ timeout: 1000 })) {
                        await todoItem.locator('.delete-btn').click();
                        await page.waitForTimeout(1000);
                        
                        const stillExistsAfterRetry = await page.locator(`#todo-${htmlTodoId}`).isVisible({ timeout: 1000 }).catch(() => false);
                        if (!stillExistsAfterRetry) {
                          console.log(`Successfully cleaned up todo on retry: "${normalizedTodoId}"`);
                          break;
                        } else {
                          console.warn(`Failed to delete todo "${normalizedTodoId}" after retry`);
                          break; // Stop trying this todo, continue with others
                        }
                      } else {
                        console.log(`Todo "${normalizedTodoId}" was deleted successfully (not visible on retry check)`);
                        break;
                      }
                    } catch (retryError) {
                      console.warn(`Failed to delete todo "${normalizedTodoId}" after retry:`, retryError);
                      break; // Stop trying this todo, continue with others
                    }
                  }
                } else {
                  console.warn(`Could not get data-todo-id for todo "${normalizedTodoId}"`);
                  break;
                }
              }
            }
          } catch (error) {
            console.warn(`Error checking todo item:`, error);
            continue;
          }
        }
        
        if (!todoFound) {
          console.warn(`Todo "${normalizedTodoId}" not found - may have been already deleted or text doesn't match exactly`);
        }
        
      } catch (error) {
        console.warn(`Failed to cleanup todo "${todoId}":`, error);
        // Continue with next todo instead of failing entire cleanup
      }
    }
    
    // Remove dialog handler
    page.off('dialog', dialogHandler);
    
  } catch (error) {
    console.warn('Failed to cleanup test todos:', error);
    // Don't throw - cleanup failures shouldn't fail tests
    // CRITICAL: Ensure dialog handler is removed even on error
    try {
      page.off('dialog', dialogHandler);
    } catch (e) {
      // Handler might already be removed, ignore
    }
  }
}

/**
 * Performs complete database cleanup for test isolation
 * Adapts behavior based on environment - full reset for clean slate, selective for persistent
 * @param page - Playwright page object
 */
export async function resetTestDatabase(page: Page): Promise<void> {
  try {
    // Navigate to home page
    await page.goto('/');
    
    // Get environment-specific cleanup configuration
    const config = await getCleanupConfig(page);
    
    // Wait for page to load
    await page.waitForTimeout(1000);
    
    // Get all existing todos
    const todoItems = await page.locator('.todo-item').all();
    
    if (todoItems.length === 0) {
      console.log('Database already empty - no cleanup needed');
      return;
    }
    
    console.log(`Found ${todoItems.length} todos to clean up for database reset`);
    console.log(`Environment mode: ${config.isCleanSlateEnvironment ? 'Clean slate (reset all)' : 'Persistent (selective cleanup)'}`);
    
    if (config.isCleanSlateEnvironment) {
      // Docker/local environment - reset everything
      const todoTexts: string[] = [];
      for (const todoItem of todoItems) {
        try {
          const todoText = await todoItem.locator('.todo-text').textContent();
          if (todoText) {
            todoTexts.push(todoText);
          }
        } catch (error) {
          console.warn('Failed to get text from todo item:', error);
        }
      }
      
      // Use existing cleanup logic to delete all todos
      await cleanupTestTodos(page, todoTexts);
    } else {
      // Kubernetes/persistent environment - use selective cleanup
      console.log('Using selective cleanup for persistent environment');
      await deleteAllUserTodos(page);
    }
    
    // Verify cleanup results
    await page.waitForTimeout(1000);
    const remainingTodos = await page.locator('.todo-item').count();
    
    if (remainingTodos === 0) {
      console.log('Database reset completed successfully - all todos removed');
    } else if (config.isCleanSlateEnvironment && remainingTodos > 0) {
      console.warn(`Database reset incomplete: ${remainingTodos} todos remain in clean slate environment`);
    } else {
      console.log(`Database cleanup completed: ${remainingTodos} todos remain (expected in persistent environment)`);
    }
    
  } catch (error) {
    console.warn('Failed to reset test database:', error);
    // Don't throw - cleanup failures shouldn't fail tests
  }
}

/**
 * Deletes a specific todo by finding it via text content
 * Returns true if deletion successful, false if todo not found
 */
export async function deleteTodoByText(page: Page, todoText: string): Promise<boolean> {
  try {
    await page.goto('/');
    
    // Normalize the input text
    const normalizedInputText = todoText.trim().replace(/\s+/g, ' ');
    
    // Find the todo item by comparing normalized text
    const allTodoItems = await page.locator('.todo-item').all();
    let targetTodoItem: any = null;
    let targetIndex = -1;
    
    for (let i = 0; i < allTodoItems.length; i++) {
      const todoItem = allTodoItems[i];
      try {
        if (!(await todoItem.isVisible({ timeout: 500 }))) {
          continue;
        }
        
        const existingText = await todoItem.locator('.todo-text').textContent();
        if (existingText) {
          const normalizedExistingText = existingText.trim().replace(/\s+/g, ' ');
          if (normalizedExistingText === normalizedInputText) {
            targetTodoItem = todoItem;
            targetIndex = i;
            console.log(`Found target todo at index ${i}: "${normalizedExistingText}"`);
            break;
          }
        }
      } catch (error) {
        continue;
      }
    }
    
    // Check if todo exists
    if (!targetTodoItem) {
      console.log(`Todo with text "${normalizedInputText}" not found - may already be deleted`);
      return false;
    }
    
    // Set up dialog handler for confirmation (works for both standard JS dialogs and some HTMX dialogs)
    const dialogHandler = (dialog: any) => dialog.accept();
    page.on('dialog', dialogHandler);
    
    try {
      // Get the todo ID for verification
      const todoId = await targetTodoItem.getAttribute('data-todo-id');
      
      // Click delete button on the specific todo
      await targetTodoItem.locator('.delete-btn').click();
      
      // Wait for HTMX to process the request
      await page.waitForTimeout(1000);
      
      // Verify deletion by checking if the specific todo ID no longer exists
      const todoStillExists = await page.locator(`#todo-${todoId}`).isVisible({ timeout: 1000 }).catch(() => false);
      
      if (!todoStillExists) {
        console.log(`Successfully deleted todo: "${normalizedInputText}"`);
        return true;
      } else {
        console.warn(`Todo "${normalizedInputText}" still visible after deletion attempt`);
        return false;
      }
    } catch (error) {
      console.warn(`Failed to delete todo "${normalizedInputText}":`, error);
      return false;
    } finally {
      // CRITICAL: Always remove dialog handler to prevent resource leaks
      page.off('dialog', dialogHandler);
    }
    
  } catch (error) {
    console.warn(`Failed to delete todo "${todoText}":`, error);
    return false;
  }
}

/**
 * Deletes all todos that appear to be user-created (containing timestamps or test patterns)
 * Adapts behavior based on environment - aggressive cleanup for shared environments
 * Returns number of todos deleted
 */
export async function deleteAllUserTodos(page: Page): Promise<number> {
  try {
    await page.goto('/');
    
    // Get environment-specific cleanup configuration
    const config = await getCleanupConfig(page);
    
    // Set up dialog handler ONCE before the loop
    const dialogHandler = (dialog: any) => dialog.accept();
    page.on('dialog', dialogHandler);
    
    let deletedCount = 0;
    let processedTodoTexts = new Set<string>(); // Track what we've already processed
    
    // Loop until no more todos to delete (handle dynamic updates)
    let maxIterations = 5; // Reduced max iterations to prevent long loops
    let iteration = 0;
    
    while (iteration < maxIterations) {
      // Get current todo items
      const todoItems = await page.locator('.todo-item').all();
      const totalTodos = todoItems.length;
      
      if (totalTodos === 0) {
        console.log('No more todos to process');
        break;
      }
      
      console.log(`Iteration ${iteration + 1}: Processing ${totalTodos} todos`);
      
      let deletedInThisIteration = 0;
      let foundNewTodosToDelete = false;
      
      // Collect all todo texts first to avoid DOM changes during iteration
      const todosToProcess: Array<{ text: string; shouldDelete: boolean }> = [];
      
      for (const todoItem of todoItems) {
        try {
          if (!(await todoItem.isVisible({ timeout: 500 }))) {
            continue;
          }
          
          const todoText = await todoItem.locator('.todo-text').textContent({ timeout: 1000 });
          
          if (todoText) {
            // Normalize whitespace and trim
            const normalizedText = todoText.trim().replace(/\s+/g, ' ');
            
            // Skip if we've already processed this exact text
            if (processedTodoTexts.has(normalizedText)) {
              console.log(`Skipping already processed todo: "${normalizedText}"`);
              continue;
            }
            
            let shouldDelete = false;
            
            if (config.requiresAggressiveCleanup) {
              // Feature branch environment - delete almost everything except very specific sample data
              const isSampleData = /^(Learn Kubernetes|Deploy microservices|Set up monitoring)$/i.test(normalizedText);
              shouldDelete = !isSampleData;
              
              if (shouldDelete) {
                console.log(`Aggressive cleanup mode: will delete "${normalizedText}" (not recognized sample data)`);
              }
            } else {
              // Docker/local environment - only delete test patterns
              const isTestTodo = /\d{13}|test|Test|TODO|todo|cleanup|Cleanup|E2E|e2e|Delete by text|Multi test|Whitespace test/i.test(normalizedText);
              shouldDelete = isTestTodo;
              
              if (shouldDelete) {
                console.log(`Conservative cleanup mode: will delete test todo "${normalizedText}"`);
              }
            }
            
            todosToProcess.push({ text: normalizedText, shouldDelete });
            
            if (shouldDelete) {
              foundNewTodosToDelete = true;
              // Mark as processed to avoid infinite loops
              processedTodoTexts.add(normalizedText);
            }
          }
        } catch (error) {
          console.warn(`Error reading todo text:`, error);
          continue;
        }
      }
      
      // If no new todos to delete found, break early
      if (!foundNewTodosToDelete) {
        console.log(`No new todos to delete found in iteration ${iteration + 1}`);
        break;
      }
      
      // Now delete the todos we identified
      for (const todoToProcess of todosToProcess) {
        if (!todoToProcess.shouldDelete) {
          continue;
        }
        
        try {
          // Find the todo by its normalized text
          const todoItem = page.locator('.todo-item').filter({ 
            hasText: new RegExp(todoToProcess.text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'))
          }).first();
          
          if (await todoItem.isVisible({ timeout: 1000 })) {
            await todoItem.locator('.delete-btn').click();
            await page.waitForTimeout(300);
            deletedCount++;
            deletedInThisIteration++;
            console.log(`Deleted todo: "${todoToProcess.text}"`);
          } else {
            console.log(`Todo "${todoToProcess.text}" no longer visible - may have been deleted`);
          }
        } catch (deleteError) {
          console.warn(`Failed to delete todo "${todoToProcess.text}":`, deleteError);
        }
      }
      
      // If we didn't delete anything in this iteration, we're done
      if (deletedInThisIteration === 0) {
        console.log('No todos were deleted in this iteration');
        break;
      }
      
      // Wait for DOM to update before next iteration
      await page.waitForTimeout(1000);
      iteration++;
    }
    
    // Remove dialog handler
    page.off('dialog', dialogHandler);
    
    console.log(`Environment: ${config.isCleanSlateEnvironment ? 'Clean slate' : 'Persistent'}, Aggressive: ${config.requiresAggressiveCleanup}, Cleaned up ${deletedCount} todos in ${iteration} iterations`);
    return deletedCount;
    
  } catch (error) {
    console.warn('Failed to clean up user todos:', error);
    return 0;
  }
}
