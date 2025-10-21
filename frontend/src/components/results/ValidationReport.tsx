"use client"

import { ValidationResult } from "@/types/api"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { ErrorCard } from "./ErrorCard"
import { WarningCard } from "./WarningCard"
import { SuccessCard } from "./SuccessCard"
import { formatDateTime } from "@/lib/utils"

interface ValidationReportProps {
  result: ValidationResult
}

export function ValidationReport({ result }: ValidationReportProps) {
  const errorCount = result.errors.filter((e) => e.severity === "error").length
  const warningCount = result.errors.filter((e) => e.severity === "warning").length
  const infoCount = result.errors.filter((e) => e.severity === "info").length

  return (
    <div className="space-y-6">
      {/* Summary Card */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Результат валідації</CardTitle>
            <Badge variant={result.isValid ? "success" : "destructive"}>
              {result.isValid ? "✓ Валідний" : "✗ Невалідний"}
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <p className="text-sm text-muted-foreground">
              Перевірено: {formatDateTime(result.validatedAt)}
            </p>
            <div className="flex flex-wrap gap-2">
              {errorCount > 0 && (
                <Badge variant="destructive">
                  {errorCount} {errorCount === 1 ? "помилка" : "помилок"}
                </Badge>
              )}
              {warningCount > 0 && (
                <Badge variant="warning">
                  {warningCount} {warningCount === 1 ? "застереження" : "застережень"}
                </Badge>
              )}
              {infoCount > 0 && (
                <Badge variant="outline">
                  {infoCount} {infoCount === 1 ? "інформаційне" : "інформаційних"}
                </Badge>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Success State */}
      {result.isValid && result.errors.length === 0 && (
        <SuccessCard message="Етикетка відповідає всім вимогам!" />
      )}

      {/* Errors */}
      {result.errors
        .filter((e) => e.severity === "error")
        .map((error, index) => (
          <ErrorCard key={`error-${index}`} error={error} />
        ))}

      {/* Warnings */}
      {result.errors
        .filter((e) => e.severity === "warning")
        .map((warning, index) => (
          <WarningCard key={`warning-${index}`} warning={warning} />
        ))}

      {/* Info */}
      {result.errors
        .filter((e) => e.severity === "info")
        .map((info, index) => (
          <Card key={`info-${index}`}>
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <span className="text-blue-500">ℹ️</span>
                {info.field}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm">{info.message}</p>
              <p className="mt-2 text-xs text-muted-foreground">
                Код: {info.code}
              </p>
            </CardContent>
          </Card>
        ))}
    </div>
  )
}

