import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

export default function CheckerPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mx-auto max-w-4xl">
        <div className="mb-8">
          <h1 className="text-3xl font-bold tracking-tight">Перевірка етикеток</h1>
          <p className="text-muted-foreground">
            Завантажте зображення етикетки або введіть текст для перевірки
          </p>
        </div>

        <div className="grid gap-6 md:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle>Завантажити файл</CardTitle>
              <CardDescription>
                Підтримуються формати: JPG, PNG, PDF
              </CardDescription>
            </CardHeader>
            <CardContent>
              {/* FileUpload component will be imported here */}
              <p className="text-muted-foreground">Компонент буде додано</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Ввести текст</CardTitle>
              <CardDescription>
                Вставте текст з етикетки для перевірки
              </CardDescription>
            </CardHeader>
            <CardContent>
              {/* TextInput component will be imported here */}
              <p className="text-muted-foreground">Компонент буде додано</p>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}

