import { createFileRoute, redirect } from "@tanstack/react-router"
import Header from "@/components/header"
import SignageForm from "@/components/signage-form"
import { useLiveQuery } from "dexie-react-hooks"
import { db } from "@/lib/db"
import type {
  CommonReferencesSchemaProps,
  SignageReferencesSchemaProps,
} from "@/schemas/references"
import { toast } from "sonner"

export const Route = createFileRoute(
  "/{-$locale}/_authenticated/data/$type/create"
)({
  beforeLoad: async () => {
    const hasDataSettings = await db.appSync.get("data")
    if (!hasDataSettings) {
      toast.info(
        <div>
          <p className="font-bold">Une mise à jour est nécessaire</p>
          <p>
            Veuillez mettre à jour les données de référentiel de saisie avant
            votre sortie de terrain.
          </p>
        </div>,
        {
          position: "top-center",
        }
      )
      throw redirect({ to: "/{-$locale}/sync" })
    }
  },
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
  const references = useLiveQuery(
    () => db.references.bulkGet([params.type, "common"]),
    [params.type]
  )

  if (
    references === undefined ||
    references[0] === undefined ||
    references[1] === undefined
  ) {
    // todo loading
    return null
  }

  return (
    <div>
      <Header title={getTitle(params.type)} withBackbutton />
      <div className="m-auto max-w-120 p-4">
        {params.type === "signage" ? (
          <SignageForm
            defaultValues={{
              id: -1,
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
              date_insert: "",
              date_update: "",
            }}
            pictogram={
              "pictogram" in references[0] ? references[0].pictogram : undefined
            }
            references={
              references as unknown as [
                SignageReferencesSchemaProps,
                CommonReferencesSchemaProps,
              ]
            }
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
