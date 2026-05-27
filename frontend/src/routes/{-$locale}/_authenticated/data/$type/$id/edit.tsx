import { createFileRoute } from "@tanstack/react-router"
import Header from "@/components/header"
import { useStoredDataElement } from "@/hook/useStoredData"
import SignageForm from "@/components/signage-form"
import type { SignageDataSchemaProps } from "@/schemas/data"

export const Route = createFileRoute(
  "/{-$locale}/_authenticated/data/$type/$id/edit"
)({
  component: RouteComponent,
})

function getTitle(type: string) {
  switch (type) {
    case "infrastructure":
      return "Modifier l'aménagement"
    case "signage":
      return "Modifier la signalétique"
    case "intervention":
      return "Modifier l'intervention"
    case "report":
      return "Modifier le signalement"
    default:
      return "Modifier l'élément"
  }
}

function RouteComponent() {
  const params = Route.useParams()
  const element = useStoredDataElement(params.type, Number(params.id))
  if (!element) {
    return (
      <div>
        <Header title={getTitle(params.type)} withBackbutton />
        <section className="m-4">
          <h2 className="mb-4 font-bold text-accent-foreground">
            Élément non trouvé
          </h2>
        </section>
      </div>
    )
  }
  return (
    <div>
      <Header title={getTitle(params.type)} withBackbutton />
      <div className="m-auto max-w-120 p-4">
        {element.reference === "signage" ? (
          <SignageForm
            element={
              element as SignageDataSchemaProps[0] & {
                pictogram: { url?: string }
                reference: string
              }
            }
          />
        ) : (
          <section>
            <h2 className="text-2xl font-medium text-accent-foreground">
              {element.name} TODO: formulaire pour "{element.reference}"
            </h2>
          </section>
        )}
      </div>
    </div>
  )
}
