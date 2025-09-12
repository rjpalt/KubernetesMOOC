import { Reporter, TestCase, TestResult, FullResult } from '@playwright/test/reporter';

class SummaryReporter implements Reporter {
  private failures: Array<{ test: TestCase; result: TestResult }> = [];
  private passes: Array<{ test: TestCase; result: TestResult }> = [];
  private skipped: Array<{ test: TestCase; result: TestResult }> = [];
  private startTime: number = 0;

  onBegin() {
    this.startTime = Date.now();
  }

  onTestEnd(test: TestCase, result: TestResult) {
    if (result.status === 'failed') {
      this.failures.push({ test, result });
    } else if (result.status === 'passed') {
      this.passes.push({ test, result });
    } else if (result.status === 'skipped') {
      this.skipped.push({ test, result });
    }
  }

  onEnd(result: FullResult) {
    const endTime = Date.now();
    const duration = ((endTime - this.startTime) / 1000).toFixed(1);
    
    console.log('\n');
    console.log('🎯 E2E Test Execution Complete');
    console.log('═'.repeat(60));
    
    // Overall statistics
    const total = this.passes.length + this.failures.length + this.skipped.length;
    const passRate = total > 0 ? ((this.passes.length / total) * 100).toFixed(1) : '0.0';
    
    console.log(`📊 Final Results:`);
    console.log(`   ✅ Passed:  ${this.passes.length}/${total} tests (${passRate}%)`);
    console.log(`   ❌ Failed:  ${this.failures.length}/${total} tests`);
    console.log(`   ⏭️  Skipped: ${this.skipped.length}/${total} tests`);
    console.log(`   ⏱️  Duration: ${duration}s`);
    
    // Show performance summary for passed tests
    if (this.passes.length > 0) {
      const avgDuration = this.passes.reduce((sum, pass) => sum + pass.result.duration, 0) / this.passes.length;
      const maxDuration = Math.max(...this.passes.map(pass => pass.result.duration));
      console.log(`   ⚡ Avg test duration: ${(avgDuration / 1000).toFixed(1)}s`);
      console.log(`   🐌 Slowest test: ${(maxDuration / 1000).toFixed(1)}s`);
    }
    
    // Show failures with details
    if (this.failures.length > 0) {
      console.log('\n🚨 Test Failures:');
      console.log('─'.repeat(60));
      
      this.failures.forEach((failure, index) => {
        const { test, result } = failure;
        console.log(`\n${index + 1}) ${test.title}`);
        console.log(`   📁 File: ${this.getRelativePath(test.location.file)}`);
        console.log(`   📍 Line: ${test.location.line}`);
        console.log(`   ⏱️  Duration: ${(result.duration / 1000).toFixed(1)}s`);
        
        if (result.error) {
          // Extract the key parts of the error message
          const errorMessage = result.error.message?.split('\n')[0] || 'Unknown error'; // First line only
          console.log(`   💥 Error: ${errorMessage}`);
          
          // Show the specific assertion failure line if available
          if (result.error.stack) {
            const lines = result.error.stack.split('\n');
            const assertionLine = lines.find(line => 
              line.includes('expect(') && (line.includes('.toBe(') || line.includes('.toHaveText(') || line.includes('.toBeVisible('))
            );
            if (assertionLine) {
              const cleanAssertion = assertionLine.trim().replace(/^\s*at\s+/, '');
              console.log(`   🔍 Assertion: ${cleanAssertion}`);
            }
            
            // Show expected vs received if it's an equality assertion
            const message = result.error.message || '';
            const expectedMatch = message.match(/Expected: (.+)/);
            const receivedMatch = message.match(/Received: (.+)/);
            if (expectedMatch && receivedMatch) {
              console.log(`   📋 Expected: ${expectedMatch[1]}`);
              console.log(`   📋 Received: ${receivedMatch[1]}`);
            }
          }
        }
        
        // Show trace/screenshot attachments if available
        if (result.attachments && result.attachments.length > 0) {
          const traces = result.attachments.filter(a => a.name === 'trace');
          const screenshots = result.attachments.filter(a => a.name === 'screenshot');
          
          if (traces.length > 0) {
            console.log(`   📊 Trace: ${this.getRelativePath(traces[0].path || '')}`);
          }
          if (screenshots.length > 0) {
            console.log(`   📸 Screenshot: ${this.getRelativePath(screenshots[0].path || '')}`);
          }
        }
      });
    }
    
    // Show summary status with execution context
    console.log('\n' + '═'.repeat(60));
    if (this.failures.length === 0) {
      console.log('🎉 All E2E tests passed successfully!');
      console.log(`🚀 Test suite completed in ${duration}s with ${this.passes.length} passing tests`);
    } else {
      console.log(`⚠️  ${this.failures.length} test(s) failed out of ${total} total tests`);
      console.log(`📝 Check failure details above for debugging information`);
      
      if (result.status === 'timedout') {
        console.log(`⏰ Test execution timed out after ${duration}s`);
      }
    }
    
    // Show overall execution status
    const overallStatus = this.failures.length === 0 ? 'PASSED' : 'FAILED';
    console.log(`🏁 Final Status: ${overallStatus}`);
    console.log('═'.repeat(60));
  }

  /**
   * Convert absolute path to relative path for cleaner display
   */
  private getRelativePath(fullPath: string): string {
    if (!fullPath) return '';
    
    // Extract just the test file name and relative path from the tests directory
    const match = fullPath.match(/tests\/e2e\/(.+)$/);
    if (match) {
      return `tests/e2e/${match[1]}`;
    }
    
    // If no match, show just the filename
    return fullPath.split('/').pop() || fullPath;
  }
}

export default SummaryReporter;
