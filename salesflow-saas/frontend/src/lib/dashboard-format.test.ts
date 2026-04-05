import { describe, expect, it } from "vitest";
import { formatSar, stageLabelAr } from "./dashboard-format";

describe("dashboard-format", () => {
  it("formats SAR", () => {
    expect(formatSar(undefined)).toBe("—");
    expect(formatSar(1200).length).toBeGreaterThan(3);
    expect(formatSar("99.5").length).toBeGreaterThan(2);
  });

  it("maps deal stages", () => {
    expect(stageLabelAr("negotiation")).toBe("تفاوض");
    expect(stageLabelAr("unknown_stage")).toBe("unknown_stage");
  });
});
