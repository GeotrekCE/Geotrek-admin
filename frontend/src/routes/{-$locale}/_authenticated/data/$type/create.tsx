import { createFileRoute } from "@tanstack/react-router"
import Header from "@/components/header"
import SignageForm from "@/components/signage-form"

export const Route = createFileRoute(
  "/{-$locale}/_authenticated/data/$type/create"
)({
  component: RouteComponent,
})

function getTitle(type: string) {
  switch (type) {
    case "infrastructure":
      return "Créer un aménagement"
    case "signage":
      return "Créer une signalétique"
    case "intervention":
      return "Créer une intervention"
    case "report":
      return "Créer un signalement"
    default:
      return "Créer un élément"
  }
}

function RouteComponent() {
  const params = Route.useParams()
  return (
    <div>
      <Header title={getTitle(params.type)} withBackbutton />
      <div className="m-auto max-w-120 p-4">
        {params.type === "signage" ? (
          <SignageForm
            defaultValues={{
              api_geom: {
                type: "Point",
                coordinates: [],
              },
              name: "",
              description: "",
              implantation_year: null,
              structure: { id: -1, name: "" },
              access: null,
              type: { id: -1, name: "" },
              conditions: [],
              code: "",
              printed_elevation: null,
              manager: null,
              sealing: null,
              blades: [],
            }}
          />
        ) : (
          <section>
            <h2 className="text-2xl font-medium text-accent-foreground">
              {getTitle(params.type)}
            </h2>
            <p>TODO: formulaire pour "{params.type}"</p>
          </section>
        )}
      </div>
    </div>
  )
}
