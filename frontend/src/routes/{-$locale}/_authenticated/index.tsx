import * as z from "zod"
import { useStoredData } from "@/hook/useStoredData"
import { createFileRoute } from "@tanstack/react-router"
import { ListProvider } from "@/lib/list"
import List from "@/components/list"
import Map from "@/components/list-map"
import Details from "@/components/list-details"
import Filters from "@/components/list-filters"
import { UpdateDataWarning } from "@/components/update-data-warning"

const focusOnItemSchema = z.object({
  id: z.number(),
  reference: z.enum(["infrastructure", "intervention", "signage", "report"]),
})

const focusOnSchema = z.preprocess(
  (value) => {
    if (typeof value !== "string") {
      return value
    }

    try {
      return JSON.parse(value)
    } catch {
      return value
    }
  },
  z
    .union([z.array(focusOnItemSchema).min(1), focusOnItemSchema])
    .transform((focusOn) => (Array.isArray(focusOn) ? focusOn : [focusOn]))
)

const schemaSearchParams = z
  .object({
    q: z.string().optional(),
    type: z
      .array(z.enum(["infrastructure", "intervention", "signage", "report"]))
      .optional(),
    focusOn: focusOnSchema.optional(),
  })
  .partial()

export type ListSearchParams = z.infer<typeof schemaSearchParams>

export const Route = createFileRoute("/{-$locale}/_authenticated/")({
  beforeLoad: UpdateDataWarning,
  component: Home,
  validateSearch: schemaSearchParams.parse,
  errorComponent: Home,
})

function Home() {
  const rawFilters = Route.useSearch()
  const filters = { ...rawFilters }

  if (rawFilters.type) {
    filters.type = rawFilters.type.filter((item) =>
      ["infrastructure", "intervention", "signage", "report"].includes(item)
    )
  }

  const elements = useStoredData(filters)

  return (
    <div className="flex h-full grow flex-col">
      <Filters filters={filters} />
      <ListProvider elements={elements} filters={filters}>
        <Map />
        <List />
        <Details />
      </ListProvider>
    </div>
  )
}
