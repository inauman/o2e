module.exports = {
  testEnvironment: 'jsdom',
  moduleNameMapper: {
    // Handle CSS imports
    '\\.(css|less|scss|sass)$': '<rootDir>/__mocks__/styleMock.js',
    // Handle image imports
    '\\.(jpg|jpeg|png|gif|webp|svg)$': '<rootDir>/__mocks__/fileMock.js',
    // Use our manual axios mock
    '^axios$': '<rootDir>/__mocks__/axios.js'
  },
  transform: {
    // Use babel-jest for ES modules and all JS/JSX/TS/TSX files
    '^.+\\.(js|jsx|ts|tsx)$': 'babel-jest'
  },
  // This is needed for handling CSS imports and image files
  transformIgnorePatterns: [
    '/node_modules/(?!.*)'
  ],
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js']
}; 