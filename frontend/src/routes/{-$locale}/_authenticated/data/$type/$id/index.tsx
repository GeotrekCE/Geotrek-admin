import * as React from "react"
import Header from "@/components/header"
import { useStoredDataElement } from "@/hook/useStoredData"
import { getLocale } from "@/paraglide/runtime"
import { createFileRoute, Link, useNavigate } from "@tanstack/react-router"
import Map from "@/components/map"
import { Marker } from "react-map-gl/maplibre"
import { Badge } from "@/components/ui/badge"
import {
  Item,
  ItemActions,
  ItemContent,
  ItemDescription,
  ItemMedia,
  ItemTitle,
} from "@/components/ui/item"
import { ChevronRight, CircleAlert, Info } from "lucide-react"
import { Button, buttonVariants } from "@/components/ui/button"
import { UpdateDataWarning } from "@/components/update-data-warning"
import { useLiveQuery } from "dexie-react-hooks"
import { db } from "@/lib/db"
import { cn } from "@/lib/utils"
import { toast } from "sonner"
import { dateCompare } from "@/lib/date"
export const Route = createFileRoute(
  "/{-$locale}/_authenticated/data/$type/$id/"
)({
  beforeLoad: UpdateDataWarning,
  component: RouteComponent,
})

function getTitle(type: string) {
  switch (type) {
    case "infrastructure":
      return "Détail aménagement"
    case "signage":
      return "Détail signalétique"
    case "intervention":
      return "Détail intervention"
    case "report":
      return "Détail signalement"
    default:
      return "Détails"
  }
}

function RouteComponent() {
  const params = Route.useParams()
  const navigate = useNavigate()
  const { type, id } = params
  const detail = useStoredDataElement(type, Number(id))
  const syncData = useLiveQuery(() => db.appSync.get("data"))

  const name =
    detail && "name" in detail ? detail.name : `Signalement (id: ${detail?.id})`

  const handleDelete = React.useCallback(() => {
    if (type === "signage") {
      // @ts-expect-error not never
      db.signageData.delete(Number(id))
    }
    if (type === "intervention") {
      // @ts-expect-error not never
      db.interventionData.delete(Number(id))
    }
    if (type === "infrastructure") {
      // @ts-expect-error not never
      db.infrastructureData.delete(Number(id))
    }
    if (type === "report") {
      // @ts-expect-error not never
      db.infrastructureData.delete(Number(id))
    }
    toast.success(`"${name}" supprimé avec succès`, { position: "top-center" })
    navigate({
      to: "/{-$locale}",
    })
  }, [type, name, navigate, id])

  if (!detail) {
    return (
      <div>
        <Header title={getTitle(type)} withBackbutton />
        <section className="m-4">
          <h2 className="mb-4 font-bold text-accent-foreground">
            Élément non trouvé
          </h2>
        </section>
      </div>
    )
  }
  const createDate = new Date(detail.date_insert).toLocaleDateString(
    getLocale()
  )
  const updateDate = new Date(detail.date_update).toLocaleDateString(
    getLocale()
  )

  const isAsyncItem = dateCompare(detail.date_update, syncData?.lastSync) > -1

  return (
    <div>
      <Header
        title={getTitle(type)}
        withBackbutton
        afterTitle={
          <Link
            className={buttonVariants({ variant: "link" })}
            to="/{-$locale}/data/$type/$id/edit"
            params={params}
          >
            Modifier
          </Link>
        }
      />
      <div className="m-auto max-w-140 p-4">
        <section>
          <h2 className="flex flex-wrap justify-between">
            <span className="text-2xl font-medium text-accent-foreground">
              {name}
            </span>
            {isAsyncItem && (
              <span className="flex items-center gap-2 text-sm text-destructive">
                <CircleAlert className="size-4" aria-hidden /> Non synchronisé
              </span>
            )}
          </h2>
          <p>
            <span className="text-primary">{params.type}</span>
            {"type" in detail && detail.type && ` - ${detail.type.name}`}
          </p>
          {"conditions" in detail && detail.conditions.length > 0 && (
            <p className="mt-1 flex flex-wrap gap-1">
              {detail.conditions.map((c) => (
                <Badge key={c.id} variant="outline">
                  {c.name}
                </Badge>
              ))}
            </p>
          )}
          <div className="mt-4">
            <p>Créé le {createDate}</p>
            {createDate !== updateDate && (
              <p>Dernière modification le {updateDate}</p>
            )}
          </div>
        </section>

        {"structure" in detail && (
          <section className="my-8">
            <h3 className="mb-2 text-xl font-bold text-accent-foreground">
              Structure liée
            </h3>
            {detail.structure ? (
              <p>{detail.structure.name}</p>
            ) : (
              <p className="italic">Aucune structure liée.</p>
            )}
          </section>
        )}

        {"description" in detail && (
          <section className="my-8">
            <h3 className="mb-2 text-xl font-bold text-accent-foreground">
              Description
            </h3>
            {detail.description ? (
              <div dangerouslySetInnerHTML={{ __html: detail.description }} />
            ) : (
              <p className="italic">Aucune description disponible.</p>
            )}
          </section>
        )}

        <section className="my-8">
          <h3 className="mb-2 text-xl font-bold text-accent-foreground">
            Localisation
          </h3>
          {detail.api_geom && (
            <Map
              className="pointer-none aspect-square max-h-80 touch-none"
              longitude={detail.api_geom.coordinates[0]}
              latitude={detail.api_geom.coordinates[1]}
            >
              <Marker
                longitude={detail.api_geom.coordinates[0]}
                latitude={detail.api_geom.coordinates[1]}
                anchor="bottom"
              />
            </Map>
          )}
        </section>

        {"blades" in detail && (
          <section className="my-8">
            <h3 className="mb-2 flex items-center gap-2 text-xl font-bold text-accent-foreground">
              Lames <Badge className="size-6">{detail.blades.length}</Badge>
            </h3>
            {"blade" in detail && detail.blades && detail.blades.length > 0 ? (
              <ul>
                {detail.blades.map((blade) => (
                  <li
                    key={blade.id}
                    className="my-2 rounded-lg border px-4 pt-2"
                  >
                    <h4>{[detail.code, blade.number].join("-")}</h4>

                    <h5 className="my-2 font-semibold">Type</h5>
                    <p>{blade.type.name}</p>

                    <h5 className="my-2 font-semibold">Conditions</h5>
                    <p>{blade.conditions.map((c) => c.name).join(", ")}</p>

                    <h5 className="my-2 font-semibold">Couleur</h5>
                    <p>{blade.color.name}</p>

                    <h5 className="my-2 font-semibold">Direction</h5>
                    <p>{blade.direction.name}</p>

                    <h5 className="my-2 font-semibold">Lignes</h5>
                    <ul>
                      {blade.lines.map((line) => (
                        <Item
                          key={line.id}
                          variant="outline"
                          className="my-4 overflow-hidden bg-accent"
                          render={
                            <button>
                              <ItemMedia className="-my-3 -ms-3 self-stretch! bg-primary/50 px-5">
                                <Info
                                  className="size-6 text-primary"
                                  aria-hidden
                                />
                              </ItemMedia>
                              <ItemContent>
                                <ItemTitle className="text-accent-foreground">
                                  {line.text}
                                </ItemTitle>
                                <ItemDescription>
                                  {line.distance} km - {line.time} h
                                </ItemDescription>
                              </ItemContent>
                              <ItemActions>
                                <ChevronRight aria-hidden />
                              </ItemActions>
                            </button>
                          }
                        />
                      ))}
                    </ul>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="italic">Aucune lame.</p>
            )}
          </section>
        )}
        {isAsyncItem && (
          <div className="mt-4 flex flex-col gap-4">
            <Link
              className={cn("w-full", buttonVariants())}
              to="/{-$locale}/data/$type/$id/edit"
              params={params}
            >
              Modifier {params.type}
            </Link>
            {dateCompare(detail.date_insert, syncData?.lastSync) > -1 && (
              <Button
                variant="destructive"
                className="w-full"
                onClick={handleDelete}
              >
                Supprimer {params.type}
              </Button>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
