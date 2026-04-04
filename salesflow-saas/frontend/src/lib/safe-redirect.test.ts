import { describe, expect, it } from "vitest";
import { safeInternalNextPath } from "./safe-redirect";

describe("safeInternalNextPath", () => {
  it("allows simple internal paths", () => {
    expect(safeInternalNextPath("/dashboard")).toBe("/dashboard");
    expect(safeInternalNextPath("/dashboard/pipeline")).toBe("/dashboard/pipeline");
  });

  it("rejects open-redirect patterns", () => {
    expect(safeInternalNextPath("//evil.com")).toBe("/dashboard");
    expect(safeInternalNextPath("//evil.com/path")).toBe("/dashboard");
    expect(safeInternalNextPath("https://evil.com")).toBe("/dashboard");
    expect(safeInternalNextPath("/\\evil")).toBe("/dashboard");
    expect(safeInternalNextPath("/path?next=https://evil.com")).toBe("/dashboard");
  });

  it("uses fallback for empty or invalid", () => {
    expect(safeInternalNextPath(null)).toBe("/dashboard");
    expect(safeInternalNextPath("")).toBe("/dashboard");
    expect(safeInternalNextPath("relative-no-slash")).toBe("/dashboard");
    expect(safeInternalNextPath("/user@host")).toBe("/dashboard");
  });

  it("accepts custom fallback", () => {
    expect(safeInternalNextPath(null, "/home")).toBe("/home");
    expect(safeInternalNextPath("//x", "/home")).toBe("/home");
  });
});
