import { PropsWithChildren } from 'react';
import { Text, View } from 'react-native';

export const CustomText = ({ children }: PropsWithChildren) => <Text>{children}</Text>;

export default function MealPlan() {
  return (
    <View>
      <CustomText>Meal Plan</CustomText>
    </View>
  );
}
