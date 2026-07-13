import { PropsWithChildren } from "react";
import { StyleSheet, Text, View } from "react-native";

export const CustomText = ({ children }: PropsWithChildren) => (
  <Text>{children}</Text>
);

export default function ShoppingList() {
  return (
    <View style={styles.container}>
      <CustomText>Shopping List</CustomText>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#fff",
    alignItems: "center",
    justifyContent: "center",
  },
});
