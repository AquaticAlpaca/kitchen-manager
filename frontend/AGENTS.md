# Testing

This is a living document. When you learn something new about testing (for
example, after examining the links listed below), update this document to ensure
that you remember the new knowledge next time.

## Test-driven development (TDD)

All feature additions, changes, and bug fixes must follow the TDD
red-green-refactor cycle. All tests, formatting, and linting must pass before a code change
is considered done.

### Front End

To test, run `npm run testOnce` from the ./frontend directory

To check formatting, run `npm run format:check` from the ./frontend directory

To lint, run `npx expo lint` from the ./frontend directory

## Expo HAS CHANGED

Read the exact versioned docs at https://docs.expo.dev/versions/v57.0.0/ before
writing any code.

## React Native Testing Library in this project

This project uses `@testing-library/react-native`. Its APIs and testing
conventions can differ from your training data. Before writing or changing RNTL
tests, read the relevant guide in
`node_modules/@testing-library/react-native/docs/`, starting with
`node_modules/@testing-library/react-native/docs/guides/llm-guidelines.md`.
Prefer those package docs over stale assumptions, and follow deprecation
notices.
