import { ValidationError } from "@/types/api"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

interface WarningCardProps {
  warning: ValidationError
}

export function WarningCard({ warning }: WarningCardProps) {
  return (
    <Card className="border-warning/50 bg-warning/5">
      <CardHeader>
        <div className="flex items-start justify-between">
          <CardTitle className="text-lg flex items-center gap-2 text-warning-700">
            <span>⚠️</span>
            {warning.field}
          </CardTitle>
          <Badge variant="warning">{warning.severity}</Badge>
        </div>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-foreground">{warning.message}</p>
        <p className="mt-2 text-xs text-muted-foreground">
          Код: {warning.code}
        </p>
      </CardContent>
    </Card>
  )
}

