import { describe, expect, it } from "vitest"

import { cn } from "./utils"

describe("cn", () => {
  it("merges class values and resolves Tailwind conflicts", () => {
    expect(cn("text-sm", "px-2", ["font-medium", "px-4"])).toBe(
      "text-sm font-medium px-4",
    )
  })
})
