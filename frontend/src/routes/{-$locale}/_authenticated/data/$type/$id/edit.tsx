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
  const { reference: _ref, pictogram, ...defaultValues } = element
  return (
    <div>
      <Header title={getTitle(params.type)} withBackbutton />
      <div className="m-auto max-w-120 p-4">
        {params.type === "signage" ? (
          <SignageForm
            defaultValues={defaultValues as SignageDataSchemaProps[0]}
            pictogram={pictogram}
            isEdit
          />
        ) : (
          <section>
            <h2 className="text-2xl font-medium text-accent-foreground">
              {defaultValues.name}
            </h2>
            <p> TODO: formulaire pour "{params.type}"</p>
          </section>
        )}
      </div>
    </div>
  )
}
