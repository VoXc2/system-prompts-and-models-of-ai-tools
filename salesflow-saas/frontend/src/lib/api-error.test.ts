import { describe, expect, it } from "vitest";
import { parseApiErrorDetail } from "./api-error";

describe("parseApiErrorDetail", () => {
  it("reads string detail", () => {
    expect(parseApiErrorDetail({ detail: "Email already registered" })).toBe("Email already registered");
  });

  it("joins FastAPI validation array", () => {
    expect(
      parseApiErrorDetail({
        detail: [{ type: "missing", loc: ["body", "phone"], msg: "Field required" }],
      })
    ).toContain("Field required");
  });
});
