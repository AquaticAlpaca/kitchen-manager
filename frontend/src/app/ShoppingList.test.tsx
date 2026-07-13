import { render } from "@testing-library/react-native";

import ShoppingList from "@/app/ShoppingList";

describe("<ShoppingList />", () => {
  test("Text renders correctly on ShoppingList", async () => {
    const { getByText } = await render(<ShoppingList />);

    getByText("Shopping List");
  });
});
