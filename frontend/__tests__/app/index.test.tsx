import { render, screen } from '@testing-library/react-native';
import Index from '@/app/index';

describe('index', () => {
  test('index shows a title', async () => {
    await render(<Index />);
    expect(screen.getByText('Kitchen Manager'));
  });
});
