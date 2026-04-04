import { describe, expect, it } from "vitest";
import {
  DEALIX_SESSION_COOKIE,
  buildLoginUrlWithNext,
  cookieHeaderHasDealixSession,
  dealixSessionCookieValueIsActive,
} from "./auth-gate";

describe("dealixSessionCookieValueIsActive", () => {
  it("accepts only literal 1", () => {
    expect(dealixSessionCookieValueIsActive("1")).toBe(true);
    expect(dealixSessionCookieValueIsActive(undefined)).toBe(false);
    expect(dealixSessionCookieValueIsActive(null)).toBe(false);
    expect(dealixSessionCookieValueIsActive("")).toBe(false);
    expect(dealixSessionCookieValueIsActive("true")).toBe(false);
    expect(dealixSessionCookieValueIsActive("0")).toBe(false);
  });
});

describe("cookieHeaderHasDealixSession", () => {
  it("finds dealix flag among other cookies", () => {
    expect(cookieHeaderHasDealixSession("foo=bar; dealix_has_session=1; x=y")).toBe(true);
    expect(cookieHeaderHasDealixSession(`other=1; ${DEALIX_SESSION_COOKIE}=1`)).toBe(true);
  });

  it("rejects missing or wrong value", () => {
    expect(cookieHeaderHasDealixSession("")).toBe(false);
    expect(cookieHeaderHasDealixSession("dealix_has_session=0")).toBe(false);
    expect(cookieHeaderHasDealixSession("dealix_has_session=")).toBe(false);
    expect(cookieHeaderHasDealixSession(undefined)).toBe(false);
  });
});

describe("buildLoginUrlWithNext", () => {
  it("sets next to pathname", () => {
    const u = buildLoginUrlWithNext("https://app.example.com/dashboard", "/dashboard/pipeline");
    expect(u.pathname).toBe("/login");
    expect(u.searchParams.get("next")).toBe("/dashboard/pipeline");
  });

  it("works with request-like base URL", () => {
    const u = buildLoginUrlWithNext("http://127.0.0.1:3000/foo", "/dashboard");
    expect(u.origin).toBe("http://127.0.0.1:3000");
    expect(u.searchParams.get("next")).toBe("/dashboard");
  });
});
