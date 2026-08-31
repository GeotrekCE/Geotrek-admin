import { Link } from "@tanstack/react-router"
import { buttonVariants } from "@/components/ui/button"
import Header from "@/components/header"
import { cn } from "@/lib/utils"

export default function NotFound() {
  return (
    <div>
      <Header title="Page non trouvée" withBackbutton />
      <section className="m-4">
        <h2 className="text-2xl font-medium text-accent-foreground">
          La page demandée n'existe pas ou plus
        </h2>
        <p>
          Retourner à la{" "}
          <Link
            to="/{-$locale}"
            className={cn(buttonVariants({ variant: "link" }), "p-0")}
          >
            page d'accueil
          </Link>
          .
        </p>
      </section>
    </div>
  )
}
