import * as React from "react"
import Header from "@/components/header"
import { getLocale } from "@/paraglide/runtime"
import { Link, useNavigate } from "@tanstack/react-router"
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
import { useLiveQuery } from "dexie-react-hooks"
import { db } from "@/lib/db"
import { cn } from "@/lib/utils"
import { toast } from "sonner"
import NotFound from "@/components/not-found"
import { usePermission } from "@/hook/useSettingsQuery"
import type { SignageDataSchemaProps } from "@/schemas/data"
import { m } from "@/paraglide/messages"

export default function SignageDetail(params: { id: string; type: string }) {
  const navigate = useNavigate()

  const [detail, loaded] = useLiveQuery(
    () =>
      db.signageData
        .get({ id: Number(params.id) })
        .then((data) => [data, true]),
    [],
    []
  )
  const rawDataItem = useLiveQuery(() =>
    db.rawData
      .where({
        reference: "signage",
        id: params.id ? Number(params.id) : undefined,
      })
      .first()
  )

  const handleDelete = React.useCallback(() => {
    // @ts-expect-error not never
    db.signageData.delete(Number(params.id))
    toast.success(`"${detail?.name}" supprimé avec succès`, {
      position: "top-center",
    })
    navigate({
      to: "/{-$locale}",
    })
  }, [detail?.name, navigate, params.id])

  const { can_bypass_structure, is_superuser } = usePermission()

  if (!loaded) {
    return null
  }

  if (!detail) {
    return <NotFound />
  }

  const createDate = new Date(detail.date_insert).toLocaleDateString(
    getLocale()
  )
  const updateDate = new Date(detail.date_update).toLocaleDateString(
    getLocale()
  )

  const isAsyncItem = detail.appSynced === false

  return (
    <div>
      <Header
        title={m["content.details.signage"]()}
        withBackbutton
        afterTitle={
          <Link
            className={buttonVariants({ variant: "link" })}
            to="/{-$locale}/data/$type/$id/edit"
            params={params}
          >
            {m["common.edit"]()}
          </Link>
        }
      />
      <div className="m-auto max-w-140 p-4">
        <section>
          <h2 className="flex flex-wrap justify-between">
            <span className="text-2xl font-medium text-accent-foreground">
              {detail.name}
            </span>
            {isAsyncItem && (
              <span className="flex items-center gap-2 text-sm text-destructive">
                <CircleAlert className="size-4" aria-hidden />{" "}
                {m["content.not-synced"]()}
              </span>
            )}
          </h2>
          <p>
            <span className="text-primary">{m["content.signage"]()}</span>
            {detail.type && ` - ${detail.type.name}`}
          </p>
          {detail.conditions.length > 0 && (
            <p className="mt-1 flex flex-wrap gap-1">
              {detail.conditions.map((c) => (
                <Badge key={c.id} variant="outline">
                  {c.name}
                </Badge>
              ))}
            </p>
          )}
          <div className="mt-4">
            <p>
              {m["content.created-on"]()} {createDate}
            </p>
            {createDate !== updateDate && (
              <p>
                {m["content.updated-on"]()} {updateDate}
              </p>
            )}
          </div>
        </section>

        {can_bypass_structure && is_superuser && (
          <section className="my-8">
            <h3 className="mb-2 text-xl font-bold text-accent-foreground">
              {m["content.linked-structure"]()}
            </h3>
            {detail.structure ? (
              <p>{detail.structure.name}</p>
            ) : (
              <p className="italic">{m["content.no-linked-structure"]()}</p>
            )}
          </section>
        )}

        <section className="my-8">
          <h3 className="mb-2 text-xl font-bold text-accent-foreground">
            {m["content.description"]()}
          </h3>
          {detail.description ? (
            <div dangerouslySetInnerHTML={{ __html: detail.description }} />
          ) : (
            <p className="italic">{m["content.no-description"]()}</p>
          )}
        </section>

        <section className="my-8">
          <h3 className="mb-2 text-xl font-bold text-accent-foreground">
            {m["content.location"]()}
          </h3>
          {detail.geom && (
            <Map
              className="pointer-none aspect-square touch-none"
              longitude={detail.geom.coordinates[0]}
              latitude={detail.geom.coordinates[1]}
            >
              <Marker
                longitude={detail.geom.coordinates[0]}
                latitude={detail.geom.coordinates[1]}
                anchor="bottom"
              />
            </Map>
          )}
        </section>

        <section className="my-8">
          <h3 className="mb-2 text-xl font-bold text-accent-foreground">
            {m["content.implantation-year"]()}
          </h3>
          {detail.implantation_year ? (
            <p>{detail.implantation_year}</p>
          ) : (
            <p className="italic">{m["content.no-implantation-year"]()}</p>
          )}
        </section>

        <section className="my-8">
          <h3 className="mb-2 text-xl font-bold text-accent-foreground">
            {m["content.code"]()}
          </h3>
          {detail.code ? (
            <p>{detail.code}</p>
          ) : (
            <p className="italic">{m["content.no-code"]()}</p>
          )}
        </section>

        <section className="my-8">
          <h3 className="mb-2 text-xl font-bold text-accent-foreground">
            {m["content.displayed-elevation"]()}
          </h3>
          {detail.printed_elevation ? (
            <p>{detail.printed_elevation}</p>
          ) : (
            <p className="italic">{m["content.no-displayed-elevation"]()}</p>
          )}
        </section>

        <section className="my-8">
          <h3 className="mb-2 text-xl font-bold text-accent-foreground">
            {m["content.manager"]()}
          </h3>
          {detail.manager ? (
            <p>{detail.manager.name}</p>
          ) : (
            <p className="italic">{m["content.no-manager"]()}</p>
          )}
        </section>

        <section className="my-8">
          <h3 className="mb-2 text-xl font-bold text-accent-foreground">
            {m["content.sealing"]()}
          </h3>
          {detail.sealing ? (
            <p>{detail.sealing.name}</p>
          ) : (
            <p className="italic">{m["content.no-sealing"]()}</p>
          )}
        </section>

        <section className="my-8">
          <h3 className="mb-2 text-xl font-bold text-accent-foreground">
            {m["content.access"]()}
          </h3>
          {detail.access ? (
            <p>{detail.access.name}</p>
          ) : (
            <p className="italic">{m["content.no-access"]()}</p>
          )}
        </section>

        <section className="my-8">
          <h3 className="mb-2 flex items-center gap-2 text-xl font-bold text-accent-foreground">
            {m["content.blades"]()}{" "}
            <Badge className="size-6">{detail.blades.length}</Badge>
          </h3>
          {detail.blades && detail.blades.length > 0 ? (
            <ul>
              {detail.blades.map((blade) => (
                <li key={blade.id} className="my-2 rounded-lg border px-4 pt-2">
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
            <p className="italic">{m["content.no-blades"]()}</p>
          )}
        </section>

        {isAsyncItem && (
          <div className="mt-4 flex flex-col gap-4">
            <Link
              className={cn("w-full", buttonVariants())}
              to="/{-$locale}/data/$type/$id/edit"
              params={params}
            >
              {m["common.edit-item"]({ item: m["content.signage"]() })}
            </Link>
            {detail.appNewItem === true && (
              <Button
                variant="destructive"
                className="w-full"
                onClick={handleDelete}
              >
                {m["common.delete-item"]({ item: m["content.signage"]() })}
              </Button>
            )}
            {rawDataItem && (
              <Button
                type="button"
                variant="destructive"
                onClick={async () => {
                  await db.rawData
                    .where({ reference: "signage", id: rawDataItem.id })
                    .delete()
                  const { reference: _reference, ...restoredData } = rawDataItem
                  await db.signageData.put(
                    restoredData as SignageDataSchemaProps
                  )
                  toast.success(m["content.restore-complete"](), {
                    position: "top-center",
                  })
                }}
              >
                {m["content.restore-pending"]()}
              </Button>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
