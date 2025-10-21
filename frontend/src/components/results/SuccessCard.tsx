import { Card, CardContent } from "@/components/ui/card"

interface SuccessCardProps {
  message: string
}

export function SuccessCard({ message }: SuccessCardProps) {
  return (
    <Card className="border-success/50 bg-success/5">
      <CardContent className="pt-6">
        <div className="flex items-center gap-3">
          <span className="text-2xl">✅</span>
          <p className="text-lg font-medium text-success">{message}</p>
        </div>
      </CardContent>
    </Card>
  )
}

