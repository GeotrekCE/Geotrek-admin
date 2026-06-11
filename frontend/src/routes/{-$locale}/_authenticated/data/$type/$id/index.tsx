import Header from "@/components/header"
import { useStoredDataElement } from "@/hook/useStoredData"
import { getLocale } from "@/paraglide/runtime"
import { createFileRoute, Link } from "@tanstack/react-router"
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
import { ChevronRight, Info } from "lucide-react"
import { buttonVariants } from "@/components/ui/button"
export const Route = createFileRoute(
  "/{-$locale}/_authenticated/data/$type/$id/"
)({
  component: RouteComponent,
})

function getTitle(type: string) {
  switch (type) {
    case "infrastructure":
      return "Détails aménagement"
    case "signage":
      return "Détails signalétique"
    case "intervention":
      return "Détails intervention"
    case "report":
      return "Détails signalement"
    default:
      return "Détails"
  }
}

function RouteComponent() {
  const params = Route.useParams()
  const element = useStoredDataElement(params.type, Number(params.id))
  if (!element) {
    return (
      <div>
        <Header title={getTitle(params.type)} withBackbutton />
        <section className="m-4">
          <h2 className="mb-4 font-bold text-accent-foreground">
            Élément non trouvé
          </h2>
        </section>
      </div>
    )
  }
  const createDate = new Date(element.date_insert).toLocaleDateString(
    getLocale()
  )
  const updateDate = new Date(element.date_update).toLocaleDateString(
    getLocale()
  )

  return (
    <div>
      <Header
        title={getTitle(params.type)}
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
      <div className="m-auto max-w-120 p-4">
        <section>
          <h2 className="text-2xl font-medium text-accent-foreground">
            {element.name}
          </h2>
          <p>
            <span className="text-primary">{element.reference}</span>
            {"type" in element && ` - ${element.type.name}`}
          </p>
          {"conditions" in element && element.conditions.length > 0 && (
            <p className="mt-1 flex flex-wrap gap-1">
              {element.conditions.map((c) => (
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

        {"structure" in element && (
          <section className="my-8">
            <h3 className="mb-2 text-xl font-bold text-accent-foreground">
              Structure liée
            </h3>
            {element.structure ? (
              <p>{element.structure.name}</p>
            ) : (
              <p className="italic">Aucune structure liée.</p>
            )}
          </section>
        )}

        {"description" in element && (
          <section className="my-8">
            <h3 className="mb-2 text-xl font-bold text-accent-foreground">
              Description
            </h3>
            {element.description ? (
              <div dangerouslySetInnerHTML={{ __html: element.description }} />
            ) : (
              <p className="italic">Aucune description disponible.</p>
            )}
          </section>
        )}

        <section className="my-8">
          <h3 className="mb-2 text-xl font-bold text-accent-foreground">
            Localisation
          </h3>
          {element.api_geom && (
            <Map
              className="pointer-none aspect-square max-h-80 touch-none"
              longitude={element.api_geom.coordinates[0]}
              latitude={element.api_geom.coordinates[1]}
            >
              <Marker
                longitude={element.api_geom.coordinates[0]}
                latitude={element.api_geom.coordinates[1]}
                anchor="bottom"
              />
            </Map>
          )}
        </section>

        {"blades" in element && (
          <section className="my-8">
            <h3 className="mb-2 flex items-center gap-2 text-xl font-bold text-accent-foreground">
              Lames <Badge className="size-6">{element.blades.length}</Badge>
            </h3>
            {element.blades && element.blades.length > 0 ? (
              <ul>
                {element.blades.map((blade) => (
                  <li
                    key={blade.id}
                    className="my-2 rounded-lg border px-4 pt-2"
                  >
                    <h4>{[element.code, blade.number].join("-")}</h4>

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
      </div>
    </div>
  )
}
