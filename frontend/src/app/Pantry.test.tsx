import { render } from "@testing-library/react-native";

import Pantry from "@/app/Pantry";

describe("<Pantry />", () => {
  test("Text renders correctly on Pantry", async () => {
    const { getByText } = await render(<Pantry />);

    getByText("Pantry");
  });
});
