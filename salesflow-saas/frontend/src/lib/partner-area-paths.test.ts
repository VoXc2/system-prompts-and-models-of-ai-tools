import { describe, expect, it } from "vitest";
import { isPartnerRestrictedPath } from "./partner-area-paths";

describe("isPartnerRestrictedPath", () => {
  it("marks marketer and asset paths", () => {
    expect(isPartnerRestrictedPath("/marketers")).toBe(true);
    expect(isPartnerRestrictedPath("/marketers/team")).toBe(true);
    expect(isPartnerRestrictedPath("/resources")).toBe(true);
    expect(isPartnerRestrictedPath("/strategy")).toBe(true);
    expect(isPartnerRestrictedPath("/dealix-marketing/index.html")).toBe(true);
    expect(isPartnerRestrictedPath("/dealix-presentations/foo")).toBe(true);
  });

  it("leaves public marketing shell open", () => {
    expect(isPartnerRestrictedPath("/")).toBe(false);
    expect(isPartnerRestrictedPath("/login")).toBe(false);
    expect(isPartnerRestrictedPath("/partner-gate")).toBe(false);
    expect(isPartnerRestrictedPath("/help")).toBe(false);
    expect(isPartnerRestrictedPath("/investors")).toBe(false);
  });
});
