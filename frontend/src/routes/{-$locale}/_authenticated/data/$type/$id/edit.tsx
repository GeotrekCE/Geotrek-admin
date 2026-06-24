import { createFileRoute } from "@tanstack/react-router"
import Header from "@/components/header"
import { useStoredDataElement } from "@/hook/useStoredData"
import SignageForm from "@/components/signage-form"
import type { SignageDataSchemaProps } from "@/schemas/data"
import { useLiveQuery } from "dexie-react-hooks"
import { db } from "@/lib/db"
import type {
  CommonReferencesSchemaProps,
  SignageReferencesSchemaProps,
} from "@/schemas/references"
import { UpdateDataWarning } from "@/components/update-data-warning"

export const Route = createFileRoute(
  "/{-$locale}/_authenticated/data/$type/$id/edit"
)({
  beforeLoad: UpdateDataWarning,
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
  const detail = useStoredDataElement(params.type, Number(params.id))
  const references = useLiveQuery(
    () => db.references.bulkGet([params.type, "common"]),
    [params.type]
  )

  if (!detail) {
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

  if (
    references === undefined ||
    references[0] === undefined ||
    references[1] === undefined
  ) {
    // todo loading
    return null
  }

  const name = "name" in detail ? detail.name : `Signalement (id: ${detail.id})`

  return (
    <div>
      <Header title={getTitle(params.type)} withBackbutton />
      <div className="m-auto max-w-120 p-4">
        {params.type === "signage" ? (
          <SignageForm
            defaultValues={detail as SignageDataSchemaProps}
            pictogram={
              "pictogram" in references[0] ? references[0].pictogram : undefined
            }
            references={
              references as unknown as [
                SignageReferencesSchemaProps,
                CommonReferencesSchemaProps,
              ]
            }
            isEdit
          />
        ) : (
          <section>
            <h2 className="text-2xl font-medium text-accent-foreground">
              {name}
            </h2>
            <p> TODO: formulaire pour "{params.type}"</p>
          </section>
        )}
      </div>
    </div>
  )
}
