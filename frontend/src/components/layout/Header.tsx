import Link from "next/link"

export function Header() {
  return (
    <header className="border-b">
      <div className="container mx-auto flex h-16 items-center justify-between px-4">
        {/* Logo Link */}
        <Link href="/" className="text-xl font-bold">
          LabelCheck UA
        </Link>
        
        {/* Navigation */}
        <nav className="flex gap-6">
          <Link 
            href="/generator" 
            className="text-sm font-medium text-muted-foreground hover:text-primary transition-colors"
          >
            Генератор
          </Link>
          <Link 
            href="/checker" 
            className="text-sm font-medium text-muted-foreground hover:text-primary transition-colors"
          >
            Перевірка
          </Link>
        </nav>
      </div>
    </header>
  )
}
