import { Link } from "@tanstack/react-router"
import { buttonVariants } from "@/components/ui/button"
import Header from "@/components/header"
import { cn } from "cn"

export default function NotAllowed() {
  return (
    <div>
      <Header title="Page non autorisée" withBackbutton />
      <section className="m-4">
        <h2 className="text-2xl font-medium text-accent-foreground">
          Vous n'avez pas les droits suffisant pour consulter cette page
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
