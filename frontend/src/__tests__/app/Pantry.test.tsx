import { render } from "@testing-library/react-native";

import Pantry from "@/app/Pantry";

describe("<Pantry />", () => {
  test("Text renders correctly on Pantry", async () => {
    (await render(<Pantry />)).getByText("Pantry");
  });
});
