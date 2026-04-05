import { describe, expect, it } from "vitest";
import { isValidSaMobile, normalizeSaMobileDigits } from "./auth-form-validation";

describe("isValidSaMobile", () => {
  it("accepts common Saudi formats", () => {
    expect(isValidSaMobile("0501234567")).toBe(true);
    expect(isValidSaMobile("501234567")).toBe(true);
    expect(isValidSaMobile("966501234567")).toBe(true);
  });

  it("rejects invalid", () => {
    expect(isValidSaMobile("")).toBe(false);
    expect(isValidSaMobile("123")).toBe(false);
  });
});

describe("normalizeSaMobileDigits", () => {
  it("normalizes to 966 prefix", () => {
    expect(normalizeSaMobileDigits("0501234567")).toBe("966501234567");
    expect(normalizeSaMobileDigits("966501234567")).toBe("966501234567");
  });
});
