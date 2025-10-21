import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

interface ResultPageProps {
  params: {
    id: string
  }
}

export default function ResultPage({ params }: ResultPageProps) {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mx-auto max-w-4xl">
        <div className="mb-8">
          <h1 className="text-3xl font-bold tracking-tight">Результати перевірки</h1>
          <p className="text-muted-foreground">
            ID перевірки: {params.id}
          </p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Звіт про валідацію</CardTitle>
            <CardDescription>
              Детальна інформація про результати перевірки
            </CardDescription>
          </CardHeader>
          <CardContent>
            {/* ValidationReport component will be imported here */}
            <p className="text-muted-foreground">Звіт буде додано</p>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

