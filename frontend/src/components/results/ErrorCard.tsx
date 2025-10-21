import { ValidationError } from "@/types/api"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

interface ErrorCardProps {
  error: ValidationError
}

export function ErrorCard({ error }: ErrorCardProps) {
  return (
    <Card className="border-error/50 bg-error/5">
      <CardHeader>
        <div className="flex items-start justify-between">
          <CardTitle className="text-lg flex items-center gap-2 text-error">
            <span>❌</span>
            {error.field}
          </CardTitle>
          <Badge variant="destructive">{error.severity}</Badge>
        </div>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-foreground">{error.message}</p>
        <p className="mt-2 text-xs text-muted-foreground">
          Код помилки: {error.code}
        </p>
      </CardContent>
    </Card>
  )
}

