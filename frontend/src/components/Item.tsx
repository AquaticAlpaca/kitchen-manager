import { Text, View } from 'react-native';

interface ItemProps {
  name: string;
  quantity: string;
  location: string;
  ordered: boolean;
}

export function Item({ name, quantity, location, ordered }: ItemProps) {
  return (
    <View>
      <Text>{name}</Text>
      <Text>Quantity: {quantity}</Text>
      <Text>{location}</Text>
    </View>
  );
}
