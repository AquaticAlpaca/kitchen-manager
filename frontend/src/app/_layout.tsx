// NOTE: This component is not directly tested because it requires
// Expo Router's runtime context. Instead, we test the individual
// pages/routes that render within this layout.
import { Stack } from 'expo-router';

export default function RootLayout() {
  return <Stack />;
}
