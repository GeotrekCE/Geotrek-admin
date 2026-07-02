import * as z from "zod"
import { useStoredData } from "@/hook/useStoredData"
import { createFileRoute } from "@tanstack/react-router"
import { ListProvider } from "@/lib/list"
import List from "@/components/list"
import Map from "@/components/list-map"
import Details from "@/components/list-details"
import Filters from "@/components/list-filters"
import { UpdateDataWarning } from "@/components/update-data-warning"

const schemaSearchParams = z
  .object({
    q: z.string().optional(),
    type: z
      .array(z.enum(["infrastructure", "intervention", "signage", "report"]))
      .optional(),
    focusOn: z
      .object({
        id: z.number(),
        reference: z.string(),
      })
      .optional(),
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
