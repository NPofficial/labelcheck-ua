"use client"

import { useState } from "react"
import { IngredientsFormProps } from "@/types/forms"
import { Ingredient } from "@/types/label"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { UNITS } from "@/lib/constants"

export function IngredientsForm({
  initialData,
  onSubmit,
  onNext,
  onBack,
}: IngredientsFormProps) {
  const [ingredients, setIngredients] = useState<Ingredient[]>(
    initialData || [
      { name: "", quantity: "", unit: "мг", isActive: true },
    ]
  )

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit(ingredients)
    onNext?.()
  }

  const addIngredient = () => {
    setIngredients([
      ...ingredients,
      { name: "", quantity: "", unit: "мг", isActive: false },
    ])
  }

  const removeIngredient = (index: number) => {
    setIngredients(ingredients.filter((_, i) => i !== index))
  }

  const updateIngredient = (index: number, field: keyof Ingredient, value: string | boolean) => {
    const updated = [...ingredients]
    updated[index] = { ...updated[index], [field]: value }
    setIngredients(updated)
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {ingredients.map((ingredient, index) => (
        <Card key={index}>
          <CardContent className="pt-6">
            <div className="space-y-4">
              <div className="flex items-center gap-2">
                <Input
                  placeholder="Назва інгредієнта"
                  value={ingredient.name}
                  onChange={(e) => updateIngredient(index, "name", e.target.value)}
                  required
                />
                <label className="flex items-center gap-2 whitespace-nowrap">
                  <input
                    type="checkbox"
                    checked={ingredient.isActive}
                    onChange={(e) => updateIngredient(index, "isActive", e.target.checked)}
                    className="h-4 w-4"
                  />
                  <span className="text-sm">Активний</span>
                </label>
              </div>

              <div className="flex items-center gap-2">
                <Input
                  type="text"
                  placeholder="Кількість"
                  value={ingredient.quantity}
                  onChange={(e) => updateIngredient(index, "quantity", e.target.value)}
                  required
                />
                <select
                  value={ingredient.unit}
                  onChange={(e) => updateIngredient(index, "unit", e.target.value)}
                  className="flex h-10 rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                >
                  {UNITS.map((unit) => (
                    <option key={unit} value={unit}>
                      {unit}
                    </option>
                  ))}
                </select>
                {ingredients.length > 1 && (
                  <Button
                    type="button"
                    variant="destructive"
                    size="sm"
                    onClick={() => removeIngredient(index)}
                  >
                    Видалити
                  </Button>
                )}
              </div>
            </div>
          </CardContent>
        </Card>
      ))}

      <Button type="button" variant="outline" onClick={addIngredient}>
        Додати інгредієнт
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

