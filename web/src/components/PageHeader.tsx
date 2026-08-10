interface PageHeaderProps {
  title: string;
  caption?: string;
}

export function PageHeader({ title, caption }: PageHeaderProps) {
  return (
    <header className="mb-8">
      <h1 className="text-3xl font-extrabold tracking-tight text-ink md:text-4xl">
        {title}
      </h1>
      {caption ? <p className="mt-2 max-w-2xl text-muted">{caption}</p> : null}
    </header>
  );
}
