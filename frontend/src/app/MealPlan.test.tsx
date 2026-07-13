import { render } from "@testing-library/react-native";

import MealPlan from "@/app/MealPlan";

describe("<MealPlan />", () => {
  test("Text renders correctly on MealPlan", async () => {
    const { getByText } = await render(<MealPlan />);

    getByText("MealPlan");
  });
});
