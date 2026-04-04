import Link from "next/link";
import clsx from "clsx";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

type Props = {
  source: string;
  backHref: string;
  backLabel: string;
  downloadPath: string;
  dir: "rtl" | "ltr";
};

const proseBase =
  "markdown-handbook mt-10 space-y-4 text-slate-200 [&_a]:text-teal-400 [&_a]:underline [&_h1]:mb-4 [&_h1]:text-balance [&_h1]:text-3xl [&_h1]:font-black [&_h1]:tracking-tight [&_h1]:text-white [&_h2]:mt-10 [&_h2]:text-2xl [&_h2]:font-bold [&_h2]:text-white [&_h3]:mt-8 [&_h3]:text-lg [&_h3]:font-semibold [&_h3]:text-teal-200 [&_hr]:my-10 [&_hr]:border-white/15 [&_li]:my-2 [&_li]:leading-relaxed [&_ol]:list-decimal [&_ol]:space-y-2 [&_p]:leading-relaxed [&_strong]:font-semibold [&_strong]:text-white [&_ul]:list-disc [&_ul]:space-y-2 [&_table]:my-6 [&_table]:w-full [&_table]:table-fixed [&_table]:border-collapse [&_table]:overflow-hidden [&_table]:rounded-xl [&_table]:border [&_table]:border-white/15 [&_thead]:bg-white/[0.06] [&_th]:border [&_th]:border-white/15 [&_th]:px-3 [&_th]:py-2.5 [&_th]:text-sm [&_th]:font-semibold [&_th]:text-white [&_td]:border [&_td]:border-white/10 [&_td]:px-3 [&_td]:py-2.5 [&_td]:text-sm";

export function MarketingMdDoc({ source, backHref, backLabel, downloadPath, dir }: Props) {
  const isRtl = dir === "rtl";
  return (
    <div className="min-h-screen bg-[#030712] text-slate-100">
      <div className="mx-auto max-w-3xl px-6 py-10 md:py-14">
        <div className="flex flex-wrap items-center justify-between gap-4 border-b border-white/10 pb-6">
          <Link
            href={backHref}
            className="text-sm font-semibold text-teal-400 transition hover:text-teal-300"
          >
            {backLabel}
          </Link>
          <a
            href={downloadPath}
            download
            className="text-xs text-slate-500 underline-offset-2 hover:text-slate-400 hover:underline"
          >
            تنزيل الملف الأصلي (.md)
          </a>
        </div>

        <article
          dir={dir}
          className={clsx(
            proseBase,
            "overflow-x-auto",
            isRtl
              ? "text-right [&_h1]:text-right [&_h2]:text-right [&_h3]:text-right [&_ol]:ps-6 [&_ul]:ps-6"
              : "text-left [&_ol]:ps-6 [&_ul]:ps-6"
          )}
        >
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{source}</ReactMarkdown>
        </article>
      </div>
    </div>
  );
}
