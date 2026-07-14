import { PropsWithChildren } from 'react';
import { Text, View } from 'react-native';

export const CustomText = ({ children }: PropsWithChildren) => <Text>{children}</Text>;

export default function Pantry() {
  return (
    <View>
      <CustomText>Pantry</CustomText>
    </View>
  );
}
