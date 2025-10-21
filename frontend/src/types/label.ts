export interface ProductInfo {
  name: string
  manufacturer: string
  dosageForm: string
  strength: string
}

export interface Ingredient {
  name: string
  quantity: string
  unit: string
  isActive: boolean
}

export interface Dosage {
  population: string
  instruction: string
  frequency: string
  duration: string
}

export interface Warning {
  type: "contraindication" | "precaution" | "side_effect" | "interaction"
  severity: "high" | "medium" | "low"
  description: string
}

export interface OperatorInfo {
  name: string
  licenseNumber: string
  productionDate: string
  expiryDate: string
  batchNumber: string
}

export interface LabelData {
  productInfo: ProductInfo
  ingredients: Ingredient[]
  dosages: Dosage[]
  warnings: Warning[]
  operatorInfo: OperatorInfo
}

