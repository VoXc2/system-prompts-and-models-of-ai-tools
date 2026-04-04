/** يطابق `playwright.config.ts` — المنفذ 3001 لتفادي تعارض مع خدمات على 3000. */
export const TEST_ORIGIN = `http://127.0.0.1:${process.env.PW_PORT || "3001"}`;
