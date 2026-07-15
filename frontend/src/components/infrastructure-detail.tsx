import * as React from "react"
import Header from "@/components/header"
import { getLocale } from "@/paraglide/runtime"
import { Link, useNavigate } from "@tanstack/react-router"
import Map from "@/components/map"
import { Marker } from "react-map-gl/maplibre"
import { Badge } from "@/components/ui/badge"
import { CircleAlert } from "lucide-react"
import { Button, buttonVariants } from "@/components/ui/button"
import { useLiveQuery } from "dexie-react-hooks"
import { db } from "@/lib/db"
import { cn } from "@/lib/utils"
import { toast } from "sonner"
import NotFound from "@/components/not-found"
import { usePermission } from "@/hook/useSettingsQuery"
import type { InfrastructureDataSchemaProps } from "@/schemas/data"
import { m } from "@/paraglide/messages"

export default function InfrastructureDetail(params: {
  id: string
  type: string
}) {
  const navigate = useNavigate()

  const [detail, loaded] = useLiveQuery(
    () =>
      db.infrastructureData
        .get({ id: Number(params.id) })
        .then((data) => [data, true]),
    [],
    []
  )

  const rawDataItem = useLiveQuery(() =>
    db.rawData
      .where({
        reference: "infrastructure",
        id: params.id ? Number(params.id) : undefined,
      })
      .first()
  )

  const handleDelete = React.useCallback(() => {
    // @ts-expect-error not never
    db.infrastructureData.delete(Number(params.id))
    toast.success(m["common.delete-success"]({ item: detail?.name ?? "" }), {
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
        title={m["content.details.infrastructure"]()}
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
                <CircleAlert className="size-4" aria-hidden />
                {m["content.not-synced"]()}
              </span>
            )}
          </h2>
          <p>
            <span className="text-primary">
              {m["content.infrastructure"]()}
            </span>
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
            {m["content.accessibility"]()}
          </h3>
          {detail.accessibility ? (
            <div dangerouslySetInnerHTML={{ __html: detail.accessibility }} />
          ) : (
            <p className="italic">{m["content.no-accessibility"]()}</p>
          )}
        </section>

        <section className="my-8">
          <h3 className="mb-2 text-xl font-bold text-accent-foreground">
            {m["content.usage-level"]()}
          </h3>
          {detail.usage_difficulty ? (
            <p>{detail.usage_difficulty.name}</p>
          ) : (
            <p className="italic">{m["content.no-usage-level"]()}</p>
          )}
        </section>

        <section className="my-8">
          <h3 className="mb-2 text-xl font-bold text-accent-foreground">
            {m["content.maintenance-level"]()}
          </h3>
          {detail.maintenance_difficulty ? (
            <p>{detail.maintenance_difficulty.name}</p>
          ) : (
            <p className="italic">{m["content.no-maintenance-level"]()}</p>
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

        {isAsyncItem && (
          <div className="mt-4 flex flex-col gap-4">
            <Link
              className={cn("w-full", buttonVariants())}
              to="/{-$locale}/data/$type/$id/edit"
              params={params}
            >
              {m["common.edit-item"]({ item: m["content.infrastructure"]() })}
            </Link>
            {detail.appNewItem === true && (
              <Button
                variant="destructive"
                className="w-full"
                onClick={handleDelete}
              >
                {m["common.delete-item"]({
                  item: m["content.infrastructure"](),
                })}
              </Button>
            )}
            {rawDataItem && (
              <Button
                type="button"
                variant="destructive"
                onClick={async () => {
                  await db.rawData
                    .where({ reference: "infrastructure", id: rawDataItem.id })
                    .delete()
                  const { reference: _reference, ...restoredData } = rawDataItem
                  await db.infrastructureData.put(
                    restoredData as InfrastructureDataSchemaProps
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
