import { createFileRoute } from "@tanstack/react-router"
import Header from "@/components/header"
import SignageForm from "@/components/signage-form"
import { useLiveQuery } from "dexie-react-hooks"
import { db } from "@/lib/db"
import type {
  CommonReferencesSchemaProps,
  InfrastructureReferencesSchemaProps,
  InterventionReferencesSchemaProps,
  SignageReferencesSchemaProps,
} from "@/schemas/references"
import InfrastructureForm from "@/components/infrastructure-form"
import InterventionForm from "@/components/intervention-form"
import { UpdateDataWarning } from "@/components/update-data-warning"

export const Route = createFileRoute(
  "/{-$locale}/_authenticated/data/$type/create"
)({
  beforeLoad: UpdateDataWarning,
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
      <div className="m-auto max-w-140 p-4">
        {params.type === "signage" && (
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
        )}
        {params.type === "infrastructure" && (
          <InfrastructureForm
            defaultValues={{
              id: -1,
              api_geom: {
                type: "Point",
                coordinates: [],
              },
              name: "",
              accessibility: "",
              description: "",
              implantation_year: null,
              structure: { id: -1, name: "" },
              access: null,
              type: { id: -1, name: "" },
              conditions: [],
              maintenance_difficulty: null,
              usage_difficulty: null,
              date_insert: "",
              date_update: "",
            }}
            pictogram={
              "pictogram" in references[0] ? references[0].pictogram : undefined
            }
            references={
              references as unknown as [
                InfrastructureReferencesSchemaProps,
                CommonReferencesSchemaProps,
              ]
            }
          />
        )}

        {params.type === "intervention" && (
          <InterventionForm
            defaultValues={{
              id: -1,
              api_geom: {
                type: "Point",
                coordinates: [],
              },
              name: "",
              description: "",
              access: null,
              structure: { id: -1, name: "" },
              type: { id: -1, name: "" },
              date_insert: "",
              date_update: "",
              begin_date: "",
              end_date: null,
              subcontracting: false,
              width: 0,
              height: 0,
              material_cost: 0,
              heliport_cost: 0,
              contractor_cost: 0,
              contractors: [],
              length: 0,
              stake: null,
              status: {
                id: -1,
                name: "",
              },
              disorders: [],
              man_day: [],
            }}
            pictogram={
              "pictogram" in references[0] ? references[0].pictogram : undefined
            }
            references={
              references as unknown as [
                InterventionReferencesSchemaProps,
                CommonReferencesSchemaProps,
              ]
            }
          />
        )}
        {!["signage", "infrastructure", "intervention"].includes(
          params.type
        ) && (
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
