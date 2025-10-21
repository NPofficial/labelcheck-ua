"use client"

import { useState } from "react"
import { WarningsFormProps } from "@/types/forms"
import { Warning } from "@/types/label"
import { Textarea } from "@/components/ui/textarea"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { WARNING_TYPES, SEVERITY_LEVELS } from "@/lib/constants"

export function WarningsForm({ initialData, onSubmit, onNext, onBack }: WarningsFormProps) {
  const [warnings, setWarnings] = useState<Warning[]>(
    initialData || [
      { type: "contraindication", severity: "high", description: "" },
    ]
  )

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit(warnings)
    onNext?.()
  }

  const addWarning = () => {
    setWarnings([
      ...warnings,
      { type: "precaution", severity: "medium", description: "" },
    ])
  }

  const removeWarning = (index: number) => {
    setWarnings(warnings.filter((_, i) => i !== index))
  }

  const updateWarning = (
    index: number,
    field: keyof Warning,
    value: string
  ) => {
    const updated = [...warnings]
    updated[index] = { ...updated[index], [field]: value }
    setWarnings(updated)
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {warnings.map((warning, index) => (
        <Card key={index}>
          <CardContent className="pt-6">
            <div className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Тип</label>
                  <select
                    value={warning.type}
                    onChange={(e) =>
                      updateWarning(index, "type", e.target.value)
                    }
                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2"
                    required
                  >
                    {Object.entries(WARNING_TYPES).map(([key, label]) => (
                      <option key={key} value={key}>
                        {label}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium">Рівень важливості</label>
                  <select
                    value={warning.severity}
                    onChange={(e) =>
                      updateWarning(index, "severity", e.target.value)
                    }
                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2"
                    required
                  >
                    {Object.entries(SEVERITY_LEVELS).map(([key, label]) => (
                      <option key={key} value={key}>
                        {label}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Опис</label>
                <Textarea
                  placeholder="Детальний опис застереження..."
                  value={warning.description}
                  onChange={(e) =>
                    updateWarning(index, "description", e.target.value)
                  }
                  required
                />
              </div>

              {warnings.length > 1 && (
                <Button
                  type="button"
                  variant="destructive"
                  size="sm"
                  onClick={() => removeWarning(index)}
                >
                  Видалити
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      ))}

      <Button type="button" variant="outline" onClick={addWarning}>
        Додати застереження
      </Button>

      <div className="flex justify-between">
        <Button type="button" variant="outline" onClick={onBack}>
          Назад
        </Button>
        <Button type="submit">Далі</Button>
      </div>
    </form>
  )
}

