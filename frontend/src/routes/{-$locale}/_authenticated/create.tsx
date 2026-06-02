import { toast } from "sonner"
import { createFileRoute, Link, redirect } from "@tanstack/react-router"
import { APP_SETTINGS_QUERY_KEY } from "@/hook/useAppSettings"
import {
  Item,
  ItemActions,
  ItemContent,
  ItemDescription,
  ItemMedia,
  ItemTitle,
} from "@/components/ui/item"
import { ChevronRight } from "lucide-react"
import { useReferencesQuery } from "@/hook/useReferencesQuery"

export const Route = createFileRoute("/{-$locale}/_authenticated/create")({
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
  component: RouteComponent,
})

function RouteComponent() {
  const { references } = useReferencesQuery()
  const elements = [
    {
      label: "Intervention",
      type: "intervention",
      description: "Ceci est un exemple d'élément à créer.",
      pictogram: references.intervention.data?.pictogram,
    },
    {
      label: "Signalétique",
      type: "signage",
      description: "Ceci est un exemple d'élément à créer.",
      pictogram: references.signage.data?.pictogram,
    },
    {
      label: "Signalement",
      type: "report",
      description: "Ceci est un exemple d'élément à créer.",
      pictogram: references.report.data?.pictogram,
    },
    {
      label: "Aménagement",
      type: "infrastructure",
      description: "Ceci est un exemple d'élément à créer.",
      pictogram: references.infrastructure.data?.pictogram,
    },
  ]
  return (
    <div className="flex grow flex-col p-4">
      <h1 className="font-bold text-accent-foreground">Nouvel élément</h1>
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
                  <ItemMedia>
                    <img loading="lazy" src={item.pictogram.url} alt="" />
                  </ItemMedia>
                  <ItemContent>
                    <ItemTitle className="text-accent-foreground">
                      {item.label}
                    </ItemTitle>
                    <ItemDescription>{item.description}</ItemDescription>
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
