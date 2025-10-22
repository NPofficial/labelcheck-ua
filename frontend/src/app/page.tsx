import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

export default function Home() {
  return (
    <div className="container mx-auto px-4 py-12">
      <div className="mx-auto max-w-4xl text-center">
        <h1 className="mb-4 text-4xl font-bold tracking-tight sm:text-5xl md:text-6xl">
          LabelCheck UA
        </h1>
        <p className="mb-8 text-lg text-muted-foreground">
          Автоматична генерація та перевірка етикеток дієтичних добавок відповідно до законодавства України
        </p>

        <div className="grid gap-6 md:grid-cols-2">
          <Card className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <CardTitle>Генератор етикеток</CardTitle>
              <CardDescription>
                Створіть правильну етикетку для вашої дієтичної добавки
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button asChild className="w-full">
                <Link href="/generator">Створити етикетку</Link>
              </Button>
            </CardContent>
          </Card>

          <Card className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <CardTitle>Перевірка етикеток</CardTitle>
              <CardDescription>
                Перевірте етикетку на відповідність законодавству
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button asChild className="w-full" variant="outline">
                <Link href="/checker">Перевірити етикетку</Link>
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}

