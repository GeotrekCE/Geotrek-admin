import { createFileRoute, Link } from "@tanstack/react-router"
import {
  Item,
  ItemActions,
  ItemContent,
  ItemDescription,
  ItemMedia,
  ItemTitle,
} from "@/components/ui/item"
import { ChevronRight } from "lucide-react"
import { db } from "@/lib/db"
import { useLiveQuery } from "dexie-react-hooks"
import type {
  InfrastructureReferencesSchemaProps,
  InterventionReferencesSchemaProps,
  ReportReferencesSchemaProps,
  SignageReferencesSchemaProps,
} from "@/schemas/references"
import { UpdateDataWarning } from "@/components/update-data-warning"
import { m } from "@/paraglide/messages"

export const Route = createFileRoute("/{-$locale}/_authenticated/create")({
  beforeLoad: UpdateDataWarning,
  component: RouteComponent,
})

function RouteComponent() {
  const references = useLiveQuery(() =>
    db.references.bulkGet([
      "intervention",
      "signage",
      "report",
      "infrastructure",
    ])
  )
  const [intervention, signage, report, infrastructure] =
    (references as
      | [
          InterventionReferencesSchemaProps,
          SignageReferencesSchemaProps,
          ReportReferencesSchemaProps,
          InfrastructureReferencesSchemaProps,
        ]
      | undefined) || []

  const elements = references?.length
    ? [
        {
          label: m["content.intervention"](),
          type: "intervention",
          description: "",
          pictogram: intervention?.pictogram,
        },
        {
          label: m["content.signage"](),
          type: "signage",
          description: "",
          pictogram: signage?.pictogram,
        },
        {
          label: m["content.report"](),
          type: "report",
          description: "",
          pictogram: report?.pictogram,
        },
        {
          label: m["content.infrastructure"](),
          type: "infrastructure",
          description: "",
          pictogram: infrastructure?.pictogram,
        },
      ]
    : []
  return (
    <div className="flex grow flex-col p-4">
      <h1 className="font-bold text-accent-foreground">
        {m["common.new-item"]()}
      </h1>
      <ul className="flex grow flex-col justify-center gap-4">
        {elements.map((item) => (
          <li key={item.type}>
            <Item
              variant="outline"
              className="bg-accent"
              render={
                <Link
                  to={`/{-$locale}/data/$type/create`}
                  params={{
                    type: item.type,
                  }}
                >
                  {item.pictogram && (
                    <ItemMedia>
                      <img loading="lazy" src={item.pictogram.url} alt="" />
                    </ItemMedia>
                  )}
                  <ItemContent>
                    <ItemTitle className="text-accent-foreground">
                      {item.label}
                    </ItemTitle>
                    {item.description && (
                      <ItemDescription>{item.description}</ItemDescription>
                    )}
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
    </div>
  )
}
