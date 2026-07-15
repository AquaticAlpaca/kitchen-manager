// https://docs.expo.dev/guides/using-eslint/
// NOTE: This component is not directly tested because the test
// would mostly be a copy of the settings listed below. Instead, we
// use this config to drive better code quality, and test that code.
const { defineConfig } = require('eslint/config');
const expoConfig = require('eslint-config-expo/flat');
const testingLibraryPlugin = require('eslint-plugin-testing-library');

module.exports = defineConfig([
  expoConfig,
  {
    ignores: ['dist/*'],
    files: ['**/__tests__/**/*.[jt]s?(x)', '**/?(*.)+(spec|test).[jt]s?(x)'],
    plugins: {
      'testing-library': testingLibraryPlugin,
    },
    rules: {
      // Add testing-library recommended rules here
      ...testingLibraryPlugin.configs.react.rules,
    },
  },
]);
