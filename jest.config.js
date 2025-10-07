module.exports = {
  testEnvironment: 'jsdom',
  testMatch: ['**/frontend/tests/**/*.test.js'],
  collectCoverageFrom: [
    'frontend/js/**/*.js',
    '!frontend/js/**/*.min.js',
  ],
  coverageDirectory: 'coverage',
  coverageReporters: ['text', 'html', 'lcov'],
  verbose: true,
  setupFilesAfterEnv: ['<rootDir>/frontend/tests/setup.js'],
};
