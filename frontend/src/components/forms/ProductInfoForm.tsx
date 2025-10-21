"use client"

import { useState } from "react"
import { ProductInfoFormProps } from "@/types/forms"
import { ProductInfo } from "@/types/label"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { DOSAGE_FORMS } from "@/lib/constants"

export function ProductInfoForm({ initialData, onSubmit, onNext }: ProductInfoFormProps) {
  const [formData, setFormData] = useState<Partial<ProductInfo>>(
    initialData || {}
  )

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (isFormValid()) {
      onSubmit(formData as ProductInfo)
      onNext?.()
    }
  }

  const isFormValid = () => {
    return (
      formData.name &&
      formData.manufacturer &&
      formData.dosageForm &&
      formData.strength
    )
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="space-y-2">
        <label htmlFor="name" className="text-sm font-medium">
          Назва препарату *
        </label>
        <Input
          id="name"
          value={formData.name || ""}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          placeholder="Наприклад: Аспірин"
          required
        />
      </div>

      <div className="space-y-2">
        <label htmlFor="manufacturer" className="text-sm font-medium">
          Виробник *
        </label>
        <Input
          id="manufacturer"
          value={formData.manufacturer || ""}
          onChange={(e) =>
            setFormData({ ...formData, manufacturer: e.target.value })
          }
          placeholder="Наприклад: Фармацевтична компанія"
          required
        />
      </div>

      <div className="space-y-2">
        <label htmlFor="dosageForm" className="text-sm font-medium">
          Лікарська форма *
        </label>
        <select
          id="dosageForm"
          value={formData.dosageForm || ""}
          onChange={(e) =>
            setFormData({ ...formData, dosageForm: e.target.value })
          }
          className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
          required
        >
          <option value="">Оберіть форму</option>
          {DOSAGE_FORMS.map((form) => (
            <option key={form} value={form}>
              {form}
            </option>
          ))}
        </select>
      </div>

      <div className="space-y-2">
        <label htmlFor="strength" className="text-sm font-medium">
          Дозування *
        </label>
        <Input
          id="strength"
          value={formData.strength || ""}
          onChange={(e) =>
            setFormData({ ...formData, strength: e.target.value })
          }
          placeholder="Наприклад: 500 мг"
          required
        />
      </div>

      <div className="flex justify-end">
        <Button type="submit" disabled={!isFormValid()}>
          Далі
        </Button>
      </div>
    </form>
  )
}

