import { render, screen } from '@testing-library/react-native';

import { Item } from '@/components/Item';

describe('<Item />', () => {
  test('displays name, quantity, and location renders correctly', async () => {
    await render(
      <Item
        name="Milk"
        quantity="1 gallon"
        location="Refrigerator"
        ordered
      />,
    );
    expect(screen.getByText('Milk')).toBeTruthy();
    expect(screen.getByText('Quantity: 1 gallon')).toBeTruthy();
    expect(screen.getByText('Refrigerator')).toBeTruthy();
  });
});
