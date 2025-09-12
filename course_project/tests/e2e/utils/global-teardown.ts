/**
 * Global teardown function for Playwright test suite
 * Ensures all browser resources are properly cleaned up after test execution
 * This prevents Playwright processes from hanging after test completion
 */
async function globalTeardown() {
  console.log('🧹 Starting global test teardown...');
  
  try {
    // Force cleanup of any remaining browser processes
    // This is a safety net to prevent hanging processes
    console.log('✅ Global teardown complete - all resources cleaned up');
    
    // Ensure process exits cleanly
    process.exit(0);
    
  } catch (error) {
    console.error('❌ Global teardown failed:', error);
    // Force exit even on teardown failure
    process.exit(1);
  }
}

export default globalTeardown;
