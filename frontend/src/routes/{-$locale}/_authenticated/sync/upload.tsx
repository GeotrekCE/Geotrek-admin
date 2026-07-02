import * as React from "react"
import { createFileRoute, Link } from "@tanstack/react-router"
import Header from "@/components/header"
import { useAsyncStoredData } from "@/hook/useStoredData"
import {
  Item,
  ItemActions,
  ItemContent,
  ItemDescription,
  ItemMedia,
  ItemTitle,
} from "@/components/ui/item"
import { ChevronRight } from "lucide-react"
import { getLocale } from "@/paraglide/runtime"
import { dateCompare, getDurationLabel } from "@/lib/date"
import type {
  InfrastructureReferencesSchemaProps,
  InterventionReferencesSchemaProps,
  ReportReferencesSchemaProps,
  SignageReferencesSchemaProps,
} from "@/schemas/references"
import { useLiveQuery } from "dexie-react-hooks"
import { db } from "@/lib/db"
import { Button } from "@/components/ui/button"
import { FetchError, queryFnWithAuth } from "@/lib/api"
import {
  type InfrastructureDataSchemaProps,
  type InterventionDataSchemaProps,
  type ReportDataSchemaProps,
  type SignageDataSchemaProps,
} from "@/schemas/data"
import { toast } from "sonner"

export const Route = createFileRoute("/{-$locale}/_authenticated/sync/upload")({
  component: RouteComponent,
})

function getBodyForMutation(
  body:
    | InfrastructureDataSchemaProps
    | SignageDataSchemaProps
    | InterventionDataSchemaProps
    | ReportDataSchemaProps
): Record<string, null | string | number | string[] | number[]> {
  return Object.fromEntries(
    Object.entries(body)
      .map(([key, value]) => {
        if (["id", "date_insert", "date_update"].includes(key)) {
          return null
        }
        if (Array.isArray(value)) {
          return [`${key}_id`, value.map((item) => item.id)]
        }
        if (value !== null && typeof value === "object" && "id" in value) {
          return [`${key}_id`, value.id]
        }
        return [key, value]
      })
      .filter((item) => item !== null)
  )
}

function RouteComponent() {
  const asyncData = useAsyncStoredData()
  const syncData = useLiveQuery(() => db.appSync.get("data"))

  const references = useLiveQuery(() =>
    db.references.bulkGet([
      "signage",
      "intervention",
      "infrastructure",
      "report",
    ])
  )
  const [signage, intervention, infrastructure, report] =
    (references as
      | [
          SignageReferencesSchemaProps,
          InterventionReferencesSchemaProps,
          InfrastructureReferencesSchemaProps,
          ReportReferencesSchemaProps,
        ]
      | undefined) || []

  const handleSubmit = React.useCallback(async () => {
    const [signageData, interventionData, infrastructureData, reportData] =
      asyncData ?? []

    const lastSync = syncData?.lastSync ?? ""
    try {
      if (signageData && signageData.length) {
        await Promise.all(
          signageData.map((body) => {
            console.log(body, getBodyForMutation(body))
            return queryFnWithAuth("/signage/drf/signages", {
              method:
                dateCompare(body.date_insert, lastSync) > -1 ? "POST" : "PATCH",
              searchParams: { format: "gtam" },
              body: JSON.stringify(getBodyForMutation(body)),
            })
          })
        )
      }
      if (interventionData && interventionData.length) {
        await Promise.all(
          interventionData.map((body) => {
            return queryFnWithAuth("/intervention/drf/interventions", {
              method:
                dateCompare(body.date_insert, lastSync) > -1 ? "POST" : "PATCH",
              searchParams: { format: "gtam" },
              body: JSON.stringify(getBodyForMutation(body)),
            })
          })
        )
      }

      if (infrastructureData && infrastructureData.length) {
        await Promise.all(
          infrastructureData.map((body) => {
            return queryFnWithAuth("/infrastructure/drf/infrastructures", {
              method:
                dateCompare(body.date_insert, lastSync) > -1 ? "POST" : "PATCH",
              searchParams: { format: "gtam" },
              body: JSON.stringify(getBodyForMutation(body)),
            })
          })
        )
      }

      if (reportData && reportData.length) {
        await Promise.all(
          reportData.map((body) => {
            return queryFnWithAuth("/report/drf/reports", {
              method:
                dateCompare(body.date_insert, lastSync) > -1 ? "POST" : "PATCH",
              searchParams: { format: "gtam" },
              body: JSON.stringify(getBodyForMutation(body)),
            })
          })
        )
      }
    } catch (error: unknown) {
      const message =
        error instanceof FetchError ? error.res.message : String(error)
      toast.error("Une erreur s'est produite", {
        position: "top-center",
        description: (
          <pre>{JSON.stringify(JSON.parse(message ?? "{}"), null, 2)}</pre>
        ),
      })
    }
  }, [asyncData, syncData?.lastSync])

  if (!asyncData) {
    return null // todo loading
  }
  const elements = asyncData
    .map((collection, index) => {
      // Signage
      if (index === 0) {
        return collection.map((item) => ({
          ...item,
          reference: "signage",
          pictogram: signage?.pictogram,
        }))
      }
      // Intervention
      if (index === 1) {
        return collection.map((item) => ({
          ...item,
          reference: "intervention",
          pictogram: intervention?.pictogram,
        }))
      }
      // Infrastructure
      if (index === 2) {
        return collection.map((item) => ({
          ...item,
          reference: "infrastructure",
          pictogram: infrastructure?.pictogram,
        }))
      }
      // Report
      if (index === 3) {
        return collection.map((item) => ({
          ...item,
          name: `Signalement (id: ${item.id})`,
          reference: "report",
          pictogram: report?.pictogram,
        }))
      }
    })
    .filter((item) => !!item)
    .flat()
    .sort((a, b) => dateCompare(b.date_update, a.date_update))

  return (
    <div>
      <Header title="Éléments non synchronisés" withBackbutton />
      <section className="m-4">
        <ul>
          {elements.length === 0 && (
            <p className="py-4 text-center">Aucun élément à afficher.</p>
          )}
          {elements.map((item) => (
            <li key={`${item.reference}-${item.id}`} className="my-4">
              <Item
                variant="outline"
                className="bg-accent"
                render={
                  <Link
                    to={`/{-$locale}/data/$type/$id`}
                    params={{
                      id: item.id.toString(),
                      type: item.reference,
                    }}
                  >
                    {item.pictogram && (
                      <ItemMedia>
                        <img loading="lazy" src={item.pictogram.url} alt="" />
                      </ItemMedia>
                    )}
                    <ItemContent>
                      <ItemTitle className="text-accent-foreground">
                        {/* @ts-expect-error report name */}
                        {item.name}
                      </ItemTitle>
                      <ItemDescription>
                        {item.reference} -{" "}
                        <time
                          dateTime={item.date_update}
                          className="text-xs text-muted-foreground"
                        >
                          {dateCompare(item.date_insert, syncData?.lastSync) >
                          -1
                            ? "Crée "
                            : "Modifié "}
                          il y a{" "}
                          {getDurationLabel(
                            new Date().getTime() -
                              new Date(item.date_update).getTime(),
                            getLocale()
                          )}
                        </time>
                      </ItemDescription>
                    </ItemContent>
                    <ItemActions>
                      <ChevronRight aria-hidden />
                    </ItemActions>
                  </Link>
                }
              />
            </li>
          ))}
        </ul>
        <Button className="w-full" onClick={handleSubmit}>
          Envoyer mes données
        </Button>
      </section>
    </div>
  )
}
