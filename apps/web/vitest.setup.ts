import "@testing-library/jest-dom/vitest";
import { afterEach } from "vitest";
import { cleanup } from "@testing-library/react";

// vitest.config.mts doesn't enable `test.globals`, so Testing Library's
// automatic afterEach(cleanup) (which relies on globals) never registers.
// Without this, DOM from one test leaks into the next.
afterEach(() => {
  cleanup();
});
