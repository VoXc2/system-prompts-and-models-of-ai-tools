export default function MarketersLoading() {
  return (
    <div className="mx-auto max-w-2xl px-6 py-16">
      <div className="h-8 w-48 animate-pulse rounded-lg bg-white/10" />
      <div className="mt-4 h-6 w-full max-w-md animate-pulse rounded-lg bg-white/5" />
      <div className="mt-10 space-y-3">
        <div className="h-24 animate-pulse rounded-2xl bg-white/5" />
        <div className="h-24 animate-pulse rounded-2xl bg-white/5" />
        <div className="h-24 animate-pulse rounded-2xl bg-white/5" />
      </div>
    </div>
  );
}
