import * as z from "zod"
import { toast } from "sonner"
import { APP_SETTINGS_QUERY_KEY } from "@/hook/useAppSettings"
import { useStoredData } from "@/hook/useStoredData"
import { createFileRoute, redirect } from "@tanstack/react-router"
import { ListProvider } from "@/lib/list"
import List from "@/components/list"
import Map from "@/components/list-map"
import Details from "@/components/list-details"
import Filters from "@/components/list-filters"

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
  beforeLoad: ({ context }) => {
    if (!context.queryClient.getQueryData(APP_SETTINGS_QUERY_KEY)) {
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
  component: Home,
  validateSearch: schemaSearchParams.parse,
})

function Home() {
  const filters = Route.useSearch()
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
