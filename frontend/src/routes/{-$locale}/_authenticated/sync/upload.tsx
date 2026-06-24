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
import { getDurationLabel } from "@/lib/date"
import type {
  InfrastructureReferencesSchemaProps,
  InterventionReferencesSchemaProps,
  ReportReferencesSchemaProps,
  SignageReferencesSchemaProps,
} from "@/schemas/references"
import { useLiveQuery } from "dexie-react-hooks"
import { db } from "@/lib/db"

export const Route = createFileRoute("/{-$locale}/_authenticated/sync/upload")({
  component: RouteComponent,
})

function RouteComponent() {
  const asyncData = useAsyncStoredData()

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
    .sort((a, b) => b.date_update.localeCompare(a.date_update))

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
                          {item.date_update === item.date_insert
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
      </section>
    </div>
  )
}
