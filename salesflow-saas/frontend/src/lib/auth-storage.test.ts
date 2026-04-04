import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { DEALIX_SESSION_COOKIE } from "./auth-gate";
import {
  clearSession,
  getAccessToken,
  getRefreshToken,
  getStoredUser,
  persistSession,
  syncSessionCookie,
} from "./auth-storage";

function stubBrowserStorage() {
  const ls = new Map<string, string>();
  const localStorageMock = {
    getItem: (k: string) => ls.get(k) ?? null,
    setItem: (k: string, v: string) => {
      ls.set(k, v);
    },
    removeItem: (k: string) => {
      ls.delete(k);
    },
  };
  vi.stubGlobal("localStorage", localStorageMock);
  vi.stubGlobal("window", { localStorage: localStorageMock });
  return ls;
}

describe("syncSessionCookie", () => {
  const assignments: string[] = [];

  beforeEach(() => {
    assignments.length = 0;
    let store = "";
    vi.stubGlobal("document", {
      get cookie() {
        return store;
      },
      set cookie(v: string) {
        assignments.push(v);
        store = v;
      },
    });
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("sets session cookie with expected name and SameSite", () => {
    syncSessionCookie(true);
    expect(assignments.length).toBeGreaterThanOrEqual(1);
    const line = assignments[0]!;
    expect(line).toContain(`${DEALIX_SESSION_COOKIE}=1`);
    expect(line).toContain("path=/");
    expect(line).toContain("SameSite=Lax");
    expect(line).toMatch(/max-age=\d+/);
  });

  it("clears session cookie when false", () => {
    syncSessionCookie(false);
    const line = assignments[0]!;
    expect(line).toContain(`${DEALIX_SESSION_COOKIE}=`);
    expect(line).toContain("max-age=0");
  });
});

describe("persistSession / clearSession", () => {
  beforeEach(() => {
    stubBrowserStorage();
    vi.stubGlobal("document", {
      set cookie(_v: string) {
        /* noop */
      },
      get cookie() {
        return "";
      },
    });
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("round-trips tokens and user JSON", () => {
    persistSession("acc", "ref", {
      userId: "u1",
      tenantId: "t1",
      role: "admin",
      email: "a@b.co",
    });
    expect(getAccessToken()).toBe("acc");
    expect(getRefreshToken()).toBe("ref");
    expect(getStoredUser()?.userId).toBe("u1");
    clearSession();
    expect(getAccessToken()).toBeNull();
    expect(getStoredUser()).toBeNull();
  });
});
