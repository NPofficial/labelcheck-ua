import { ProductInfo, Ingredient, Dosage, Warning, OperatorInfo } from "./label"

export interface ProductInfoFormProps {
  initialData?: Partial<ProductInfo>
  onSubmit: (data: ProductInfo) => void
  onNext?: () => void
}

export interface IngredientsFormProps {
  initialData?: Ingredient[]
  onSubmit: (data: Ingredient[]) => void
  onNext?: () => void
  onBack?: () => void
}

export interface DosageFormProps {
  initialData?: Dosage[]
  onSubmit: (data: Dosage[]) => void
  onNext?: () => void
  onBack?: () => void
}

export interface WarningsFormProps {
  initialData?: Warning[]
  onSubmit: (data: Warning[]) => void
  onNext?: () => void
  onBack?: () => void
}

export interface OperatorFormProps {
  initialData?: Partial<OperatorInfo>
  onSubmit: (data: OperatorInfo) => void
  onBack?: () => void
}

export type FormStep = 
  | "product-info" 
  | "ingredients" 
  | "dosage" 
  | "warnings" 
  | "operator"

