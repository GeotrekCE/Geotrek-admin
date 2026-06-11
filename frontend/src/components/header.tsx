import { useRouter } from "@tanstack/react-router"
import { ChevronLeft } from "lucide-react"
import { Button } from "@/components/ui/button"

export default function Header({
  title,
  withBackbutton,
  beforeTitle = null,
  afterTitle = null,
}: {
  beforeTitle?: React.ReactNode
  afterTitle?: React.ReactNode
  title: string
  withBackbutton?: boolean
}) {
  const router = useRouter()
  return (
    <header className="grid items-center p-4">
      {withBackbutton && (
        <div className="col-start-1 row-start-1">
          <Button
            className="relative z-1"
            onClick={() => router.history.back()}
            variant="ghost"
            size="icon"
          >
            <ChevronLeft className="size-6" aria-hidden />
            <span className="sr-only">Retour page précédente</span>
          </Button>
        </div>
      )}
      <h1 className="col-start-1 row-start-1 text-center font-bold text-accent-foreground">
        {title}
      </h1>
      {beforeTitle && (
        <div className="relative z-1 col-start-1 row-start-1">
          {beforeTitle}
        </div>
      )}
      {afterTitle && (
        <div className="relative z-1 col-start-1 row-start-1 justify-self-end">
          {afterTitle}
        </div>
      )}
    </header>
  )
}
