export function Footer() {
  const currentYear = new Date().getFullYear()

  return (
    <footer className="border-t py-6 md:py-0">
      <div className="container flex flex-col items-center justify-between gap-4 md:h-16 md:flex-row">
        <p className="text-center text-sm leading-loose text-muted-foreground md:text-left">
          © {currentYear} Label Check. Всі права захищені.
        </p>
        <div className="flex items-center space-x-4">
          <Link
            href="/about"
            className="text-sm text-muted-foreground hover:text-foreground"
          >
            Про систему
          </Link>
          <Link
            href="/docs"
            className="text-sm text-muted-foreground hover:text-foreground"
          >
            Документація
          </Link>
          <Link
            href="/contact"
            className="text-sm text-muted-foreground hover:text-foreground"
          >
            Контакти
          </Link>
        </div>
      </div>
    </footer>
  )
}

function Link({
  href,
  children,
  className,
}: {
  href: string
  children: React.ReactNode
  className?: string
}) {
  return (
    <a href={href} className={className}>
      {children}
    </a>
  )
}

